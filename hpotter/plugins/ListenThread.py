import socket
import threading
import ssl
import tempfile
import os

from OpenSSL import crypto, SSL
from time import gmtime, mktime

from hpotter import tables
from hpotter.env import logger, write_db
from hpotter.plugins.ContainerThread import ContainerThread

class ListenThread(threading.Thread):
    def __init__(self, listen_address, container_name, table=None, limit=None):
        super().__init__()
        self.listen_address = listen_address
        self.container_name = container_name
        self.table = table
        self.limit = limit
        self.shutdown_requested = False
        self.TLS = False
        self.cert_file = None
        self.key_file = None

    # https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
    def gen_cert(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)
        cert = crypto.X509()
        cert.get_subject().C = "UK"
        cert.get_subject().ST = "London"
        cert.get_subject().L = "London"
        cert.get_subject().O = "Dummy Company Ltd"
        cert.get_subject().OU = "Dummy Company Ltd"
        cert.get_subject().CN = socket.gethostname()
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha1')

        # can't use an iobyte file for this as load_cert_chain only take a
        # filesystem path :/
        self.cert_file = tempfile.NamedTemporaryFile(delete=False)
        self.cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        self.cert_file.close()

        self.key_file = tempfile.NamedTemporaryFile(delete=False)
        self.key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        self.key_file.close()

    def run(self):
        if self.TLS:
            self.gen_cert()
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self.cert_file.name, \
                keyfile=self.key_file.name)
            os.remove(self.cert_file.name)
            os.remove(self.key_file.name)

        logger.info('Listening to ' + str(self.listen_address))
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # check for shutdown request every five seconds
        listen_socket.settimeout(5)
        listen_socket.bind(self.listen_address)
        listen_socket.listen()

        while True:
            source = None
            try:
                # TODO: put the address in the connection table here
                source, address = listen_socket.accept()
                if self.TLS:
                    source = context.wrap_socket(source, server_side=True)
            except socket.timeout:
                if self.shutdown_requested:
                    logger.info('Shutdown requested')
                    break
                else:
                    continue
            except Exception as exc:
                logger.info(exc)

            logger.info('Starting a ContainerThread')
            # TODO: push on list of containers to send shutdown messages to
            ContainerThread(source, self.container_name).start()

        if listen_socket:
            listen_socket.close()
            logger.info('Socket closed')

    def request_shutdown(self):
        self.shutdown_requested = True
