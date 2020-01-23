import socket
import threading
import io
import ssl

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
        self.certificate = self.privatekey = None

    '''
    https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
    https://stackoverflow.com/questions/44672524/how-to-create-in-memory-file-object/44672691
    '''
    def gen_cert(self):
        publickey = crypto.PKey()
        publickey.generate_key(crypto.TYPE_RSA, 4096)
        cert = crypto.X509()
        cert.get_subject().C = "UK"
        cert.get_subject().ST = "London"
        cert.get_subject().L = "Diagon Alley"
        cert.get_subject().OU = "The Leaky Caldron"
        cert.get_subject().O = "J.K. Incorporated"
        cert.get_subject().CN = socket.gethostname()
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(publickey)
        cert.sign(publickey, 'sha1')
        self.certificate = \
            io.BytesIO(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        self.privatekey = \
            io.BytesIO(crypto.dump_privatekey(crypto.FILETYPE_PEM, publickey))
    
    def run(self):
        self.gen_cert()
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.certificate, keyfile=self.privatekey)

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
                source = context.wrap_socket(source, server_side=True)
            except socket.timeout:
                if self.shutdown_requested:
                    logger.info('Shutdown requested')
                    break
                else:
                    continue
            except Exception as exc:
                logger.info(exc)
                break

            logger.info('Starting a ContainerThread')
            # TODO: push on list of containers to send shutdown messages to
            ContainerThread(source, self.container_name).start()

        if listen_socket:
            listen_socket.close()
            logger.info('Socket closed')

    def request_shutdown(self):
        self.shutdown_requested = True
