import socket
import threading

from hpotter import tables
from hpotter.env import logger, write_db

# remember to put name in __init__.py

class ListenThread(threading.Thread):
    def __init__(self, bind_address, table, limit):
        super().__init__()
        self.bind_address = bind_address
        self.table = table
        self.limit = limit
        self.shutdown_requested = False

    def run(self):
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.settimeout(5)    # check for shutdown request every five seconds
        socket.bind(self.bind_address)
        socket.listen()

        while True:
            try:
                source = None
                try:
                    source, address = socket.accept()
                except socket.timeout:
                    if self.shutdown_requested:
                        logger.info('Shutdown requested')
                        break
                except Exception as exc:
                    logger.info(exc)
                    break

            ContainerThread(source).start()

        if socket:
            socket.close()
            logger.info('socket closed')

    def request_shutdown(self):
        self.shutdown_requested = True
