import socket
import threading

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

    def run(self):
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
