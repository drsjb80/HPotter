from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from framework import HPotterDB
from env import logger
from datetime import datetime
import socket
import socketserver
import threading

# remember to put name in __init__.py

# https://hg.python.org/cpython/file/2.7/Lib/SocketServer.py

# put all the simple text queries in here
qandr = {'ls': 'foo\n', \
    'more': 'bar\n'}

class ShTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    command = Column(String)

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

class ShTCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def handle(self):
        self.request.sendall('Username: ')
        username = self.request.recv(1024).strip()
        self.request.sendall('Password: ')
        password = self.request.recv(1024).strip()
        self.request.sendall('Last login: Mon Nov 20 12:41:05 2017 from ' +
            '8.8.8.8\n')
        self.request.sendall('# ')
        command = self.request.recv(1024).strip()

        entry = HPotterDB.HPotterDB (
            sourceIP=self.client_address[0], \
            sourcePort=self.client_address[1], \
            destIP=self.server.mysocket.getsockname()[0], \
            destPort=self.server.mysocket.getsockname()[1], \
            proto=HPotterDB.TCP)

        sh = ShTable(command=command, username=username, password=password)
        sh.hpotterdb = entry
        self.session.add(sh)

        if command in qandr:
            self.request.sendall(qandr[command])
        elif command == "date":
            # cheesing out and always returning UTC. should probably pick a
            # random one and pytz.
            date = datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")
            self.request.sendall(date + '\n')
        else:
            self.request.sendall('bash: ' + command + ': command not found\n')

    def finish(self):
        self.session.commit()
        self.session.close()

# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class ShServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        # save socket for use in server_bind and handler
        self.mysocket = mysocket

        # save engine for creating sessions in the handler
        self.engine = engine

        # must be called after setting mysocket as __init__ calls server_bind
        socketserver.TCPServer.__init__(self, None, ShTCPHandler)

    def server_bind(self):
        self.socket = self.mysocket

# listen to both IPv4 and v6
def get_addresses():
    return ([(socket.AF_INET, '127.0.0.1', 2300), \
        (socket.AF_INET6, '::1', 2300)])

def start_server(my_socket, engine):
    server = ShServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    return server
