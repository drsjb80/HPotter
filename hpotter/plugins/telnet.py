from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from hpotter.hpotter import qandr
import socket
import socketserver
import threading

# remember to put name in __init__.py

# https://docs.python.org/3/library/socketserver.html

class CommandTableTelnet(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    extend_existing=True
    id =  Column(Integer, primary_key=True)
    command = Column(String)
    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

class LoginTableTelnet(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

class TelnetHandler(socketserver.BaseRequestHandler):
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
        username, password = "", ""
        while True:
            character = self.request.recv(1024).decode("utf-8")
            if character == ("\r\n" or "\n" or ""):
                break
            username += character

        self.request.sendall(b'Password: ')
        while True:
            character = self.request.recv(1024).decode("utf-8")
            if character == ("\r\n" or "\n" or ""):
                break
            password += character

        login = LoginTableTelnet(username=username, password=password)
        login.hpotterdb = entry
        self.session.add(login)

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\r\n')

        self.request.sendall(b'#: ')
        command = b""
        global command_list
        command_list = []
        command_count = 0
        while True:
            character = self.request.recv(1024)
            if character.decode("utf-8") == ("\r\n" or "\n" or ""):
                if command in qandr.qandr:
                    self.request.sendall(qandr.qandr[command].encode("utf-8\r\n"))
                else:
                    self.request.sendall(b'bash: ' + command + b': command not found\r\n')
                command_list.append(command)
                command_count += 1
                if command_count > 3 or command.decode("utf-8").__contains__("exit"):
                    break
                command = b""
                self.request.sendall(b'#: ')
            else:
                command += character

        cmd = CommandTableTelnet(command=command.decode("utf-8"))
        cmd.hpotterdb = entry
        for command in command_list:
            cmd = CommandTableTelnet(command=command.decode("utf-8"))
            cmd.hpotterdb = entry
            self.session.add(cmd)

    def finish(self):
        self.session.commit()
        self.session.close()

# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class TelnetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        # save socket for use in server_bind and handler
        self.mysocket = mysocket

        # save engine for creating sessions in the handler
        self.engine = engine

        # must be called after setting mysocket as __init__ calls server_bind
        socketserver.TCPServer.__init__(self, None, TelnetHandler)

    def server_bind(self):
        self.socket = self.mysocket

# listen to both IPv4 and v6
def get_addresses():
    return ([(socket.AF_INET, '127.0.0.1', 23), \
        (socket.AF_INET6, '::1', 23)])

def start_server(my_socket, engine):
    server = TelnetServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    return server
