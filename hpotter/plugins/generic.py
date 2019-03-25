import socket
import threading

from hpotter import tables
from hpotter.env import logger, Session

# remember to put name in __init__.py

def wrap_socket(function):
    try:
        return function()
    except socket.timeout as timeout:
        logger.debug(timeout)
        raise Exception
    except socket.error as error:
        logger.debug(error)
        raise Exception
    except Exception as exc:
        logger.debug(exc)
        raise Exception

# started from: http://code.activestate.com/recipes/114642/

class OneWayThread(threading.Thread):
    def __init__(self, source, dest, table=None, limit=0):
        super().__init__()
        self.source = source
        self.dest = dest
        self.limit = limit
        self.table = table

        if self.table:
            self.session = Session()
            self.connection = tables.Connections(
                sourceIP=self.source.getsockname()[0],
                sourcePort=self.source.getsockname()[1],
                destIP=self.dest.getsockname()[0],
                destPort=self.dest.getsockname()[1],
                proto=tables.TCP)
            self.session.add(self.connection)

    def run(self):
        logger.debug('Starting timer')
        timer = threading.Timer(120, self.shutdown)
        timer.start()

        total = b''
        while 1:
            try:
                data = wrap_socket(lambda: self.source.recv(4096))
            except Exception:
                break

            if data == b'' or not data:
                break

            if self.table or self.limit > 0:
                total += data

            try:
                wrap_socket(lambda: self.dest.sendall(data))
            except Exception:
                break

            if self.limit > 0 and len(total) >= self.limit:
                break

        if self.table:
            http = self.table(request=str(total), connection=self.connection)
            self.session.add(http)
            self.session.commit()

        logger.debug('Canceling timer')
        timer.cancel()
        self.shutdown()

    def shutdown(self):
        if self.table:
            Session.remove()
        self.source.close()
        self.dest.close()

class PipeThread(threading.Thread):
    def __init__(self, bind_address, connect_address, table, limit):
        super().__init__()
        self.bind_address = bind_address
        self.connect_address = connect_address
        self.table = table
        self.limit = limit
        self.shutdown_requested = False

    def run(self):
        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source_socket.settimeout(5)
        source_socket.bind(self.bind_address)
        source_socket.listen()

        while True:
            try:
                try:
                    source, address = source_socket.accept()
                except socket.timeout:
                    if self.shutdown_requested:
                        logger.info('Shutdown requested')
                        return
                    else:
                        continue

                dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # dest.settimeout(30)
                dest.connect(self.connect_address)
    

                OneWayThread(source, dest, self.table, self.limit).start()
                OneWayThread(dest, source).start()

            except OSError as exc:
                source.close()
                logger.info(exc)
                continue

    def request_shutdown(self):
        self.shutdown_requested = True
