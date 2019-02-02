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
    def __init__(self, source, dest, capture, connection=None, limit=0):
        threading.Thread.__init__(self)
        self.source = source
        self.dest = dest
        self.capture = capture
        self.connection = connection
        self.limit = limit

    def run(self):
        threading.Timer(120, self.shutdown).start()
        session = Session()
        total = b''

        while 1:
            try:
                data = self.source.recv(4096)
            except BaseException as exc:
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

        if self.capture and self.connection:
            http = tables.HTTPCommands(request=total)
            http.connection = self.connection
            session.add(http)
            session.commit()
            Session.remove()
        self.shutdown()

    def shutdown(self):
        self.source.close()
        self.dest.close()

class HttpdThread(threading.Thread):
    def run(self):
        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source_socket.bind(('0.0.0.0', 80))
        source_socket.listen(4)

        while True:
            try:
                source, address = source_socket.accept()

                connection = tables.Connections(
                    sourceIP=address[0],
                    sourcePort=address[1],
                    destIP=source_socket.getsockname()[0],
                    destPort=source_socket.getsockname()[1],
                    proto=tables.TCP)

                dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest.connect(('172.172.172.172', 80))

                PipeThread(source, dest, True, connection, 4096).start()
                PipeThread(dest, source, False).start()

                # to avoid a DOS attack, put two joins in here and/or keep
                # track of the number of threads here. could create a list
                # and join the first when "full"
            except BaseException as exc:
                source.close()
                logger.info('HttpdThread')
                logger.info(exc)
                continue

def start_server():
    machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''
    try:
        tmpdir = tempfile.TemporaryDirectory()

        client = docker.from_env()
        hpotter.env.httpd_container = client.containers.run(machine + 'httpd', \
            detach=True, read_only=True, \
            volumes={tmpdir.name: {'bind': '/usr/local/apache2', 'mode': 'rw'}})

        logger.info('Created: %s', hpotter.env.httpd_container)

        # remove the default bridge
        network = client.networks.get('bridge')
        network.disconnect(hpotter.env.httpd_container)

        # create a network to talk across
        hpotter.env.httpd_network = client.networks.create('httpipe', \
            driver="bridge", internal=True)
        hpotter.env.httpd_network.connect(hpotter.env.httpd_container, \
            ipv4_address='172.172.172.172')

    except BaseException as exc:
        logger.info(exc)
        logger.info(hpotter.env.httpd_container.logs())
        return

    HttpdThread().start()

def stop_server():
    hpotter.env.httpd_network.disconnect(hpotter.env.httpd_container)
    hpotter.env.httpd_network.remove()
    hpotter.env.httpd_container.stop()
    hpotter.env.httpd_container.remove()
