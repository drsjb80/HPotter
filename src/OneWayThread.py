import socket
import threading

from src import tables
from src.logger import logger
from src.database import database

class OneWayThread(threading.Thread):
    def __init__(self, source, dest, connection, config, direction):
        super().__init__()
        self.source = source
        self.dest = dest
        self.config = config
        self.connection = connection
        self.config = config
        self.direction = direction

        self.length = 0
        if self.direction + '_length' in self.config:
            length = self.config[self.direction + '_length']

        self.total = b''
        self.shutdown_requested = False

    def read(self):
        logger.info(self.direction + ' reading from: ' + str(self.source))
        data = self.source.recv(4096)
        logger.info(self.direction + ' read: ' + str(data))

        return data

    def write(self, data):
        logger.info(self.direction + ' sending to: ' + str(self.dest))
        self.dest.sendall(data)
        logger.info(self.direction + ' sent: ' + str(data))

    def run(self):
        while True:
            try:
                data = self.read()
                if not data or data == b'':
                    break
                self.write(data)
            except Exception as exception:
                logger.info(self.direction + str(exception))
                break


            self.total += data

            if self.shutdown_requested:
                break

            if self.length > 0 and len(self.total) >= self.length:
                logger.debug('Length exceeded')
                break

        logger.debug(self.length)
        logger.debug(len(self.total))
        logger.debug(self.direction)
        if self.length > 0 and len(self.total) > 0:
            database.write(tables.Data(direction=self.direction, data=str(self.total), connection=self.connection))

    def shutdown(self):
        self.shutdown_requested = True
