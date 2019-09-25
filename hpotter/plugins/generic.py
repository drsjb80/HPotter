import socket, ssl
import threading

from hpotter import tables
from hpotter.env import logger, write_db

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
    def __init__(self, source, dest, table=None, limit=0, di=None):
        super().__init__()
        self.source = source
        self.dest = dest
        self.table = table
        self.limit = limit
        self.di = di

        if self.table:
            self.connection = tables.Connections(
                sourceIP=self.source.getsockname()[0],
                sourcePort=self.source.getsockname()[1],
                destPort=self.dest.getsockname()[1],
                proto=tables.TCP)
            write_db(self.connection)

    def run(self):
        total = b''
        while 1:
            try:
                data = wrap_socket(lambda: self.source.recv(4096))
                if self.dest.getsockname()[1]:
                    
                    pass
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
            if self.di:
                total = self.di(total)
            http = self.table(request=str(total), connection=self.connection)
            write_db(http)

        self.source.close()
        self.dest.close()

class PipeThread(threading.Thread):
    def __init__(self, bind_address, connect_address, table, limit, di=None):
        super().__init__()
        self.bind_address = bind_address
        self.connect_address = connect_address
        self.table = table
        self.limit = limit
        self.di = di

        self.shutdown_requested = False

    def run(self):
        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        source_socket.settimeout(5)
        source_socket.bind(self.bind_address)
        source_socket.listen()
        TLS = False #needs to pivot from plugin.py

        while True:
            try:
                source = None
                try:
                    source, address = source_socket.accept()
                    if TLS:
                        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                        context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")
                        source = context.wrap_context(source, server_side=True)
                except socket.timeout:
                    if self.shutdown_requested:
                        logger.info('Shutdown requested')
                        if source:
                            source.close()
                        logger.info('Socket closed')
                        return
                    else:
                        continue

                dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest.settimeout(30)
                dest.connect(self.connect_address)

                OneWayThread(source, dest, self.table, self.limit, \
                    di=self.di).start()
                OneWayThread(dest, source).start()

            except OSError as exc:
                dest.close()
                source.close()
                logger.info(exc)
                continue

    def request_shutdown(self):
        self.shutdown_requested = True
