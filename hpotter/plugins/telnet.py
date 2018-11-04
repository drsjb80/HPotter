from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from hpotter.hpotter.command_response import command_response
import socket
import socketserver
import threading
import unittest
from unittest.mock import Mock, call

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
    undertest = False

    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def get_string(self):
        character = self.request.recv(1)

        # where there are telnet commands
        while character == b'\xff':
            # skip the next two as they are part of the telnet command
            self.request.recv(1)
            self.request.recv(1)
            character = self.request.recv(1)

        string = ""
        while character != b'\n' and character != b'\r':
            string += character.decode("utf-8")
            character = self.request.recv(1)

        # read the newline
        if character == b'\r':
            character = self.request.recv(1)

        return string.strip()

    def trying(self, prompt):
        tries = 0
        response = ''
        while response == '':
            self.request.sendall(prompt)
            response = self.get_string()
            tries += 1
            if tries > 3:
                return ''

        return response

    def handle(self):
        entry = HPotterDB.HPotterDB (
            sourceIP=self.client_address[0], \
            sourcePort=self.client_address[1], \
            destIP=self.server.mysocket.getsockname()[0], \
            destPort=self.server.mysocket.getsockname()[1], \
            proto=HPotterDB.TCP)

        username = self.trying(b'Username: ')
        if username == '':
            return

        prompt = b'#: '
        if username == 'root' or username == 'admin':
            prompt = b'$: '

        password = self.trying(b'Password: ')
        if password == '':
            return

        login = LoginTableTelnet(username=username, password=password)
        login.hpotterdb = entry
        self.session.add(login)

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\r\n')

        command_count = 0
        while command_count < 4:
            self.request.sendall(prompt)
            command = self.get_string()
            command_count += 1

            if command == '':
                continue
            elif command == 'exit':
                break
            elif command in command_response:
                self.request.sendall(command_response[command].encode("utf-8"))
            else:
                f = command.split()[0].encode('utf-8')
                self.request.sendall(b'bash: ' + f + b': command not found\r\n')

            cmd = CommandTableTelnet(command=command)
            cmd.hpotterdb = entry
            self.session.add(cmd)

    def finish(self):
        # ugly ugly ugly
        # i need to figure out how to properly mock sessionmaker
        if not self.undertest:
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
# quad 0 allows for docker port exposure
def get_addresses():
    return [(socket.AF_INET, '0.0.0.0', 23)]


def start_server(my_socket, engine):
    server = TelnetServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    return server

class TestTelnet(unittest.TestCase):
    def setUp(self):
        TelnetHandler.undertest = True
        self.test_server = unittest.mock.Mock()
        self.test_server.mysocket = unittest.mock.Mock()
        self.test_server.mysocket.getsockname.return_value = \
            ['127.0.0.1', '2001']

    def test_TelnetHandler(self):
        tosend = "root\ntoor\nls\nfoo\nexit\n"
        test_request = unittest.mock.Mock()
        test_request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]

        TelnetHandler.session = unittest.mock.Mock()
        TelnetHandler(test_request, ['127.0.0.1', 2000], self.test_server)

        # print(test_request.mock_calls)
        test_request.sendall.assert_has_calls([call(b'Username: '),
            call(b'Password: '),
            call(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\r\n'),
            call(b'$: '),
            call(b'Servers  Databases   Top_Secret  Documents\r\n'),
            call(b'$: '),
            call(b'bash: foo: command not found\r\n'),
            call(b'$: ')])
