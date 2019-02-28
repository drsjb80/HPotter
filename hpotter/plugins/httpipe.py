import socket
import threading
import platform
import tempfile

import docker

import hpotter
from hpotter import tables
from hpotter.env import logger, Session

# remember to put name in __init__.py

# started from: http://code.activestate.com/recipes/114642/

class PipeThread(threading.Thread):
    # pylint: disable=R0913
    def __init__(self, source, dest, capture, limit=0):
        threading.Thread.__init__(self)
        self.source = source
        self.dest = dest
        self.capture = capture
        self.limit = limit
        self.session = Session()

        self.connection = tables.Connections(
            sourceIP=self.source.getsockname()[0],
            sourcePort=self.source.getsockname()[1],
            destIP=self.dest.getsockname()[0],
            destPort=self.dest.getsockname()[1],
            proto=tables.TCP)
        self.session.add(self.connection)

    def run(self):
        timer = threading.Timer(120, self.shutdown)
        timer.start()

        total = b''
        while 1:
            try:
                data = self.source.recv(4096)
            except OSError as ose:
                # closed connection
                if ose.errno != 9:
                    logger.info('recv')
                    logger.info(exc)
                break

            # logger.info(data)
            if data == b'' or not data:
                break

            if self.capture:
                total += data

            try:
                self.dest.sendall(data)
            except BaseException as exc:
                logger.info('sendall')
                logger.info(exc)
                break

            if self.limit > 0 and len(total) > self.limit:
                break

        if self.capture:
            http = tables.HTTPCommands(request=str(total))
            http.connections = self.connection
            self.session.add(http)
            self.session.commit()
            Session.remove()

        logger.info('Canceling timer')
        timer.cancel()
        self.shutdown()

    def shutdown(self):
        logger.info('PipeThread.shutdown')
        self.source.close()
        self.dest.close()

class HttpdThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.shutdown_requested = False

    def run(self):
        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source_socket.settimeout(5)
        source_socket.bind(('0.0.0.0', 80))
        source_socket.listen(4)

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
                logger.info(hpotter.env.httpd_container_address)
                dest.connect(('127.0.0.1', 8080))
                logger.info('after connect')

                PipeThread(source, dest, True, 4096).start()
                PipeThread(dest, source, False).start()

                # to avoid a DOS attack, put two joins in here and/or keep
                # track of the number of threads here. could create a list
                # and join the first when "full"
            except BaseException as exc:
                source.close()
                logger.info('HttpdThread')
                logger.info(exc)
                continue

    def request_shutdown(self):
        self.shutdown_requested = True

def start_server():
    machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''
    try:
        client = docker.from_env()

        hpotter.env.httpd_container = client.containers.run \
        ( \
            machine + 'httpd', \
            detach=True, \
            ports={'80/tcp': 8080}, \
            read_only=True, \
            volumes={'apache2': {'bind': '/usr/local/apache2', 'mode': 'rw'}} \
        )
        logger.info('Created: %s', hpotter.env.httpd_container)

    except BaseException as exc:
        logger.info(exc)
        if hpotter.env.httpd_container:
            logger.info(hpotter.env.httpd_container.logs())
        return

    hpotter.env.httpdThread = HttpdThread()
    hpotter.env.httpdThread.start()

def stop_server():
    # hpotter.env.httpd_network.disconnect(hpotter.env.httpd_container)
    # hpotter.env.httpd_network.remove()

    hpotter.env.httpdThread.request_shutdown()

    if hpotter.env.httpd_container:
        logger.info('Stopping httpd_container')
        hpotter.env.httpd_container.stop()
        logger.info('Removing httpd_container')
        hpotter.env.httpd_container.remove()
        hpotter.env.httpd_container = None
