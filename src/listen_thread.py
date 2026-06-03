"""Listen to a socket and create a container thread in response to connections.

This module implements the ListenThread class which handles incoming connections
on a specified port and spawns Container instances to handle each connection.
Called from __main__.py.
"""

import ipaddress
import os
import random
import socket
import ssl
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from src import tables
from src.container import Container
try:
    from src.ssh_container import SSHContainer
    _SSH_AVAILABLE = True
except ImportError:
    _SSH_AVAILABLE = False
from src.lazy_init import lazy_init
from src.logger import logger
from src.metrics import (
    active_connections,
    connections_started_total,
    listen_threads_total,
)

try:
    import geoip2.errors
    import geoip2.database
    READER = geoip2.database.Reader('GeoLite2/GeoLite2-City.mmdb')
except Exception as exc:
    logger.info(f'Error: {exc}, not using GeoLite2')
    READER = False


class TempCertFiles:
    """Context manager for temporary certificate files."""
    def __init__(self, cert_data, key_data):
        self.cert_data = cert_data
        self.key_data = key_data
        self.cert_path = None
        self.key_path = None

    def __enter__(self):
        # Create temporary certificate file
        with tempfile.NamedTemporaryFile(delete=False) as cert_file:
            cert_file.write(self.cert_data)
            self.cert_path = cert_file.name

        # Create temporary key file
        with tempfile.NamedTemporaryFile(delete=False) as key_file:
            key_file.write(self.key_data)
            self.key_path = key_file.name

        return self.cert_path, self.key_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up temporary files
        try:
            if self.cert_path and os.path.exists(self.cert_path):
                os.remove(self.cert_path)
        except Exception as err:
            logger.debug("Error removing temp cert file: %s", err)
        try:
            if self.key_path and os.path.exists(self.key_path):
                os.remove(self.key_path)
        except Exception as err:
            logger.debug("Error removing temp key file: %s", err)


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
        # create or load an SSL context, then harden settings to TLS1.2/1.3
        def _harden(ctx):
            # prefer at least TLS 1.2 and optionally cap at 1.3
            try:
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
                ctx.maximum_version = ssl.TLSVersion.TLSv1_3
            except AttributeError:
                # fallback if running on very old python
                ctx.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 |
                                ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
            # use a strong cipher suite list
            ctx.set_ciphers('HIGH:!aNULL:!MD5')

        if 'key_file' in self.container:
            logger.info('Reading from SSL configuration files')
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.context.verify_mode = ssl.CERT_NONE
            _harden(self.context)
            self.context.load_cert_chain(
                self.container['cert_file'],
                self.container['key_file']
            )
        else:
            logger.info('Generating self-signed SSL certificate')

            # Generate RSA private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )

            # Build a self-signed certificate with honeypot details
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "UK"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "London"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Diagon Alley"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "The Leaky Caldron"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "J.K. Incorporated"),
                x509.NameAttribute(NameOID.COMMON_NAME, socket.gethostname()),
            ])

            hostname = socket.gethostname()
            san_names = [x509.DNSName(hostname), x509.DNSName('localhost')]
            try:
                san_names.append(x509.IPAddress(ipaddress.ip_address('127.0.0.1')))
                san_names.append(x509.IPAddress(ipaddress.ip_address('::1')))
            except ValueError:
                pass
            san = x509.SubjectAlternativeName(san_names)

            serial = self.container.get('serial', random.randint(1, sys.maxsize))
            logger.debug(f'Setting certificate serial to {serial}')

            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key.public_key())
                .serial_number(serial)
                .not_valid_before(datetime.now(timezone.utc))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=10 * 365))
                .add_extension(san, critical=False)
                .sign(private_key, hashes.SHA256())
            )

            # Expose cert object for unit tests / inspection
            self.cert = cert

            # Write certificate and key to temp files and load them
            # (load_cert_chain requires filesystem paths)
            cert_data = cert.public_bytes(serialization.Encoding.PEM)
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )

            with TempCertFiles(cert_data, key_data) as (cert_path, key_path):
                self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.context.verify_mode = ssl.CERT_NONE
                _harden(self.context)
                self.context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    def _save_connection(self, address):
        """Save connection information to the database

        Args:
            address: Tuple of (ip_address, port) for the connecting client
        """
        if READER:
            logger.debug(f'Looking up geolocation for {address[0]}')
            try:
                response = READER.city(address[0])
                country = response.country.iso_code
                city = response.city.name
                latitude = response.location.latitude
                longitude = response.location.longitude
            except geoip2.errors.AddressNotFoundError:
                country = city = latitude = longitude = None
        else:
            country = city = latitude = longitude = None

        # Create connection record (with or without destination info)
        if 'save_destination' in self.container:
            destination_address = self.listen_address
            destination_port = self.listen_port
        else:
            destination_address = None
            destination_port = None

        self.connection = tables.Connections(
            destination_address=destination_address,
            destination_port=destination_port,
            source_address=address[0],
            source_port=address[1],
            latitude=latitude,
            longitude=longitude,
            city=city,
            country=country,
            container=self.container['container'],
            protocol=tables.TCP
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
        listen_threads_total.inc()
        listen_socket.listen()

        num_threads = self.container.get('threads', None)
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            while True:
                source = None
                try:
                    source, address = listen_socket.accept()

                    source.settimeout(self.container.get('socket_timeout', 10))

                    # Wrap socket with TLS if enabled
                    if self.TLS:
                        source = self.context.wrap_socket(source, server_side=True)

                    self._save_connection(address)
                    connections_started_total.inc()
                    active_connections.inc()

                except socket.timeout:
                    # Check for shutdown request on timeout
                    if self.shutdown_requested:
                        logger.info('listen_thread shutting down')
                        break
                    continue

                except Exception as exc:
                    # If SSL handshake fails we want to know the version/cipher
                    if isinstance(exc, ssl.SSLError):
                        logger.info(
                            "SSL accept error: %s version=%s reason=%s",
                            exc, getattr(exc, 'version', None),
                            getattr(exc, 'reason', None)
                        )
                    else:
                        # Else, something seriously has gone wrong.
                        logger.info(f'Error accepting connection: {exc}')
                    if source:
                        source.close()
                    continue

                # Create and submit container handler to handle connection
                if self.container.get('type') == 'ssh':
                    if not _SSH_AVAILABLE:
                        logger.error('SSH type requested but paramiko is unavailable')
                        source.close()
                        continue
                    thread = SSHContainer(
                        source,
                        self.connection,
                        self.container,
                        self.database
                    )
                else:
                    thread = Container(
                        source,
                        self.connection,
                        self.container,
                        self.database
                    )
                # Container no longer subclasses Thread; submit its
                # ``run`` method directly to the pool.
                future = executor.submit(self._run_container_thread, thread)
                self.container_list.append((future, thread))
                self._prune_completed_containers()

        listen_threads_total.dec()
        listen_socket.close()

    def _run_container_thread(self, thread):
        try:
            thread.run()
        finally:
            active_connections.dec()

    def _prune_completed_containers(self):
        self.container_list = [
            (future, thread)
            for future, thread in self.container_list
            if not future.done()
        ]

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
