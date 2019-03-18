import socket
import threading

import docker

import hpotter
from hpotter import tables
from hpotter.env import logger, Session

# remember to put name in __init__.py

# started from: http://code.activestate.com/recipes/114642/

class OneWayThread(threading.Thread):
    # pylint: disable=R0913
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
                data = self.source.recv(4096)
            except IOError as err:
                # 9 = time out
                if err.errno != 9:
                    logger.info(err)
                break;
            except Exception as exc:
                logger.info(exc)
                break

            if data == b'' or not data:
                break

            if self.table:
                total += data

            try:
                self.dest.sendall(data)
            except OSError as exc:
                logger.info(exc)
                break

            if self.limit > 0 and len(total) > self.limit:
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
                        return
                    else:
                        continue

                dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest.settimeout(5)
                dest.connect(self.connect_address)

                OneWayThread(source, dest, self.table, self.limit).start()
                OneWayThread(dest, source).start()

            except OSError as exc:
                source.close()
                logger.info(exc)
                continue

    def request_shutdown(self):
        self.shutdown_requested = True

def rm_container():
    if hpotter.env.httpd_container:
        logger.info('Stopping httpd_container')
        hpotter.env.httpd_container.stop()
        logger.info('Removing httpd_container')
        hpotter.env.httpd_container.remove()
        hpotter.env.httpd_container = None
    else:
        logger.info('No httpd_container to stop')

def start_server():     # leave these two in place
    # machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''
    try:
        client = docker.from_env()

        # create apache2 or random dir?
        hpotter.env.httpd_container = client.containers.run('httpd:latest', \
            detach=True, ports={'80/tcp': 8080}, read_only=True, \
            volumes={'apache2': {'bind': '/usr/local/apache2', 'mode': 'rw'}})
        logger.info('Created: %s', hpotter.env.httpd_container)

    except OSError as err:
        logger.info(err)
        if hpotter.env.httpd_container:
            logger.info(hpotter.env.httpd_container.logs())
            rm_container()
        return

    hpotter.env.httpdThread = PipeThread(('0.0.0.0', 80), \
        ('127.0.0.1', 8080), tables.HTTPCommands, 4096)
    hpotter.env.httpdThread.start()

def stop_server():
    hpotter.env.httpdThread.request_shutdown()
    rm_container()
