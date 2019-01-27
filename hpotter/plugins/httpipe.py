from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import connectiontable
from hpotter.env import logger, Session

from socket import *
import threading
import platform
import docker

# remember to put name in __init__.py

class HTTPTable(connectiontable.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    request = Column(String)

    connectiontable_id = Column(Integer, ForeignKey('connectiontable.id'))
    connectiontable = relationship("ConnectionTable")

# started from: http://code.activestate.com/recipes/114642/

class PipeThread(threading.Thread):
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
            http = HTTPTable(request=total)
            http.connection = self.connection
            session.add(http)
            session.commit()
            Session.remove()
        self.shutdown()

    def shutdown(self):
        self.source.close()
        self.dest.close()

class httpdThread(threading.Thread):
    def run(self):
        source_socket = socket(AF_INET, SOCK_STREAM)
        source_socket.bind(('0.0.0.0', 80))
        source_socket.listen(4)

        while True:
            try:
                source, address = source_socket.accept()

                connection = connectiontable.ConnectionTable(
                    sourceIP=address[0],
                    sourcePort=address[1],
                    destIP=source_socket.getsockname()[0],
                    destPort=source_socket.getsockname()[1],
                    proto=connectiontable.TCP)

                dest = socket(AF_INET, SOCK_STREAM)
                dest.connect(('localhost', 8080))

                # capture the queries,
                t1 = PipeThread(source, dest, True, connection, 4096).start()
                # not the responses.
                t2 = PipeThread(dest, source, False).start()

                # to avoid a DOS attack, put two joins in here and/or keep
                # track of the number of threads here. could create a list
                # and join the first when "full"
            except BaseException as exc:
                source.close()
                logger.info('httpdThread')
                logger.info(exc)
                continue

httpdserver_thread = None
httpd_container = None

def start_server():
    global httpd_container
    machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''
    try:
        client = docker.from_env()
        httpd_container = client.containers.run(machine + 'httpd', 
            ports={'80/tcp': 8080}, detach=True, read_only=True, 
            volumes={'/tmp/apache2': {'bind': '/usr/local/apache2',
                'mode': 'rw'}})
        logger.info('Created:' + str(httpd_container))
    except BaseException as exc:
        logger.info(exc)
        logger.info(httpd_container.logs())
        return

    global httpdserver_thread
    httpdserver_thread = httpdThread()
    httpdserver_thread.start()

def stop_server():
    httpd_container.stop()
    httpd_container.remove()

def get_container():
    pass
