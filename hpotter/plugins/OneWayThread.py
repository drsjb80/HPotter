import socket
import threading

from hpotter.tables import Data
from hpotter.logger import logger
from hpotter.db import write_db

# read and write between two sockets with a possible upper limit. write to
# db if table passed in.
class OneWayThread(threading.Thread):
    def __init__(self, source, dest, config, kind):
        super().__init__()
        self.source = source
        self.dest = dest
        self.config = config
        self.kind = kind
        self.shutdown_requested = False

    def run(self):
        save = False
        if self.kind:
            s = self.kind + '_length'
            if s in self.config and self.config[s] > 0:
                save = True
                length = self.config[s]

        total = b''
        while 1:
            try:
                data = self.source.recv(4096)
            except Exception as exception:
                logger.info(exception)
                break

            logger.debug('Reading from: ' + str(self.source) + ', read: ' + str(data))

            if data == b'' or not data:
                logger.debug('No data read, stopping')
                break

            if self.shutdown_requested:
                break

            if save:
                total += data

            try:
                self.dest.sendall(data)
            except Exception as exception:
                logger.info(exception)
                break
            logger.debug('Sending to: ' + str(self.dest) + ', sent: ' + str(data))

            if self.shutdown_requested:
                break

            if save and len(total) >= length:
                logger.debug('Limit exceeded, stopping')
                break

        if save and len(total) > 0:
            write_db(Data(data=str(total), kind=self.kind, connection=self.connection))

    def shutdown(self):
        self.shutdown_requested = True
