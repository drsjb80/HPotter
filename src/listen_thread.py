"""Listen to a socket and create a container thread in response to connections.

This module implements the ListenThread class which handles incoming connections
on a specified port and spawns ContainerThread instances to handle each connection.
Called from __main__.py.
"""

import os
import random
import socket
import ssl
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

import psutil
from geolite2 import geolite2
from OpenSSL import crypto

from src import tables
from src.container_thread import ContainerThread
from src.lazy_init import lazy_init
from src.logger import logger

READER = geolite2.reader()

class ListenThread(threading.Thread):
    """Thread that listens for incoming connections and spawns container threads.

    Attributes:
        container: Configuration dict for the honeypot container
        database: Database instance for storing connection info
        shutdown_requested: Flag to signal thread shutdown
        TLS: Whether TLS/SSL is enabled
        context: SSL context for TLS connections
        container_list: List of spawned container threads and futures
        connection: Current connection being handled
        listen_address: Address to bind to
        listen_port: Port to listen on
    """

    @lazy_init
    def __init__(self, container, database):
        super().__init__()

        # Set default save options
        self.container.setdefault('request_save', True)
        self.container.setdefault('response_save', False)

        self.shutdown_requested = False
        self.TLS = self.container.get('TLS', False)
        self.context = None
        self.container_list = []
        self.connection = None
        self.listen_address = self.container.get('listen_address', '')
        self.listen_port = self.container['listen_port']

    def _gen_cert(self):
        """Generate or load SSL/TLS certificate for secure connections.

        If key_file is specified in container config, loads existing certs.
        Otherwise, generates a self-signed certificate dynamically.

        Reference: https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
        """
        if 'key_file' in self.container:
            logger.info('Reading from SSL configuration files')
            self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.context.load_cert_chain(
                self.container['cert_file'],
                self.container['key_file']
            )
        else:
            logger.info('Generating self-signed SSL certificate')

            # Generate RSA private key
            key = crypto.PKey()
            key.generate_key(crypto.TYPE_RSA, 4096)

            # Create X509 certificate with honeypot details
            cert = crypto.X509()
            cert.get_subject().C = "UK"
            cert.get_subject().ST = "London"
            cert.get_subject().L = "Diagon Alley"
            cert.get_subject().OU = "The Leaky Caldron"
            cert.get_subject().O = "J.K. Incorporated"
            cert.get_subject().CN = socket.gethostname()

            # Set serial number (random or from config)
            serial = self.container.get('serial', random.randint(1, sys.maxsize))
            logger.debug(f'Setting certificate serial to {serial}')
            cert.set_serial_number(serial)

            # Set validity period (10 years)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(key)
            cert.sign(key, 'sha1')

            # Write certificate and key to temp files
            # (load_cert_chain requires filesystem paths)
            with tempfile.NamedTemporaryFile(delete=False) as cert_file:
                cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
                cert_path = cert_file.name

            with tempfile.NamedTemporaryFile(delete=False) as key_file:
                key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
                key_path = key_file.name

            # Load the certificate chain
            self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.context.load_cert_chain(certfile=cert_path, keyfile=key_path)

            # Clean up temporary files
            os.remove(cert_path)
            os.remove(key_path)

    def _save_connection(self, address):
        """Save connection information to the database with geolocation data.

        Args:
            address: Tuple of (ip_address, port) for the connecting client
        """
        latitude = None
        longitude = None

        # Look up geolocation data for the source IP
        info = READER.get(address[0])
        if info and 'location' in info:
            location = info['location']
            if 'latitude' in location and 'longitude' in location:
                latitude = str(location['latitude'])
                longitude = str(location['longitude'])

        # Create connection record (with or without destination info)
        if 'save_destination' in self.container:
            self.connection = tables.Connections(
                destination_address=self.listen_address,
                destination_port=self.listen_port,
                source_address=address[0],
                source_port=address[1],
                latitude=latitude,
                longitude=longitude,
                container=self.container['container'],
                protocol=tables.TCP
            )
        else:
            self.connection = tables.Connections(
                source_address=address[0],
                source_port=address[1],
                latitude=latitude,
                longitude=longitude,
                container=self.container['container'],
                proto=tables.TCP
            )

        self.database.write(self.connection)

    def _create_listen_socket(self):
        """Create and configure the listening socket.

        Returns:
            Configured socket bound to the listen address and port
        """
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Check for shutdown request every 5 seconds
        listen_socket.settimeout(5)

        listen_address = (self.listen_address, self.listen_port)
        logger.info('Listening on %s', listen_address)
        listen_socket.bind(listen_address)
        return listen_socket

    def run(self):
        """Main thread execution loop - accepts connections and spawns handlers."""
        if self.TLS:
            self._gen_cert()

        listen_socket = self._create_listen_socket()
        listen_socket.listen()

        num_threads = self.container.get('threads', None)
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            while True:
                source = None
                try:
                    source, address = listen_socket.accept()

                    # Log current file descriptor count for monitoring
                    logger.debug(f'Open file descriptors: {psutil.Process().num_fds()}')

                    # Wrap socket with TLS if enabled
                    if self.TLS:
                        source = self.context.wrap_socket(source, server_side=True)

                    source.settimeout(self.container.get('connection_timeout', 10))
                    self._save_connection(address)

                except socket.timeout:
                    # Check for shutdown request on timeout
                    if self.shutdown_requested:
                        logger.info('listen_thread shutting down')
                        break
                    continue

                except Exception as exc:
                    logger.error(f'Error accepting connection: {exc}')
                    sys.exit(0)

                # Create and submit container thread to handle connection
                thread = ContainerThread(
                    source,
                    self.connection,
                    self.container,
                    self.database
                )
                future = executor.submit(thread.start)
                self.container_list.append((future, thread))

        listen_socket.close()

    def shutdown(self):
        """Shut down all container threads created by this listener.

        Called externally to gracefully terminate all active connections
        and their associated handler threads.
        """
        logger.info('listen_thread shutdown called')
        self.shutdown_requested = True
        for future, container_thread in self.container_list:
            if future.running():
                container_thread.shutdown()
