import socket
import threading
import io

from OpenSSL import crypto, SSL
from time import gmtime, mktime

from hpotter import tables
from hpotter.env import logger, write_db
from hpotter.plugins.ContainerThread import ContainerThread

# remember to put name in __init__.py

class ListenThread(threading.Thread):
    def __init__(self, bind_address, table=None, limit=None):
        super().__init__()
        self.bind_address = bind_address
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
        cert.get_subject().L = "London"
        cert.get_subject().O = "Dummy Company Ltd"
        cert.get_subject().OU = "Dummy Company Ltd"
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
        logger.info('Listening to ' + str(self.bind_address))
        bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_socket.settimeout(5)    # check for shutdown request every five seconds
        bind_socket.bind(self.bind_address)
        bind_socket.listen()

        while True:
            source = None
            try:
                source, address = bind_socket.accept()
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
            ContainerThread(source).start()

        if bind_socket:
            bind_socket.close()
            logger.info('Socket closed')

    def request_shutdown(self):
        self.shutdown_requested = True
