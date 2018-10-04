from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from datetime import datetime
import socket
import socketserver
import threading

# remember to put name in __init__.py

# https://docs.python.org/3/library/socketserver.html

# put all the simple text queries in here
qandr = {b'ls': 'foo\n', \
    b'more': 'bar\n'}

class CommandTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    command = Column(String)

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

class LoginTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

class ShTCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def handle(self):
        entry = HPotterDB.HPotterDB (
            sourceIP=self.client_address[0], \
            sourcePort=self.client_address[1], \
            destIP=self.server.mysocket.getsockname()[0], \
            destPort=self.server.mysocket.getsockname()[1], \
            proto=HPotterDB.TCP)

        self.request.sendall(b'Username: ')
        username = self.request.recv(1024).strip().decode("utf-8")
        self.request.sendall(b'Password: ')
        password = self.request.recv(1024).strip().decode("utf-8")

        login = LoginTable(username=username, password=password)
        login.hpotterdb = entry
        self.session.add(login)

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\n')
        self.request.sendall(b'# ')

        command = self.request.recv(1024).strip()

        cmd = CommandTable(command=command.decode("utf-8"))
        cmd.hpotterdb = entry
        self.session.add(cmd)

        if command in qandr:
            self.request.sendall(qandr[command].encode("utf-8"))
        elif command == b"date":
            # cheesing out and always returning UTC. should probably pick a
            # random one and pytz.
            date = datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")
            self.request.sendall(date.encode("utf-8") + b'\n')
        else:
            self.request.sendall(b'bash: ' + command + b': command not found\n')

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
