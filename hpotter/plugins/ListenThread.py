import socket
import threading

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

    def run(self):
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
