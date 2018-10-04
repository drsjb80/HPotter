from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from datetime import datetime
import socket
import paramiko
import socketserver
import threading
from paramiko.py3compat import u, decodebytes
from binascii import hexlify
import sys

host_key = paramiko.RSAKey(filename="RSAKey.cfg")
# Replace qandr with Inna's Command Response Script
qandr = {b'ls': 'foo',
         b'more': 'bar',
         b'date': datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")}


class CommandTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    command = Column(String)

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")


class LoginTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")


class SSHHandler:
    def __init__(self, server, chan):
        self.server = server
        self.chan = chan

    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def handle(self):
        entry = HPotterDB.HPotterDB(
            sourceIP=self.chan.get_transport().getpeername()[0],
            sourcePort=self.chan.get_transport().getpeername()[1],
            destIP=self.server.mysocket.getsockname()[0],
            destPort=self.server.mysocket.getsockname()[1],
            proto=HPotterDB.TCP)
        login = LoginTable(username=attack_username, password=attack_password)
        login.hpotterdb = entry
        self.session.add(login)

        for command in command_list:
            cmd = CommandTable(command=command.decode("utf-8"))
            cmd.hpotterdb = entry
            self.session.add(cmd)

    def finish(self):
        self.session.commit()
        self.session.close()


class SSHServer(socketserver.ThreadingMixIn, socketserver.TCPServer, paramiko.ServerInterface):
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        self.mysocket = mysocket
        self.engine = engine
        socketserver.TCPServer.__init__(self, None, None)
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        global attack_username, attack_password
        attack_username, attack_password = username, password
        # changed so that any username/password can be used
        if username and password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print("Auth attempt with key: " + u(hexlify(key.get_fingerprint())))
        if username == 'exit':
            sys.exit(1)
        if(username == "user") and (key == self.good_pub_key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    # Turned off, causing problems
    def enable_auth_gssapi(self):
        return False

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
            self, channel, term, width, height, pixelwidth, pixelheight,
            modes):
        return True

    def server_bind(self):
        self.socket = self.mysocket


# listen to both IPv4 and v6
def get_addresses():
    return ([(socket.AF_INET, '127.0.0.1', 22),
             (socket.AF_INET6, '::1', 22)])


def client_handler(my_socket):
    my_socket.listen(100)
    client, addr = my_socket.accept()
    transport = paramiko.Transport(client)
    return transport


def start_server(my_socket, engine):
    transport = client_handler(my_socket)
    transport.load_server_moduli()
    transport.add_server_key(host_key)
    server = SSHServer(my_socket, engine)
    transport.start_server(server=server)
    return server, transport


def channel_handler(transport, server):
    chan = transport.accept(20)
    if chan is None:
        print("*** No channel.")
        sys.exit(1)
    send_ssh_introduction(chan)
    receive_client_data(chan)
    write_to_database(server, chan)
    chan.close()


def send_ssh_introduction(chan):
    chan.send("\r\nChannel Open!\r\n")
    chan.send("\r\nNOTE:")
    chan.send("\r\nType \"exit\" when finished\r\n")
    chan.send("\r\nLast login: Whatever you want it to be")
    chan.send("\r\n# ")


def write_to_database(server, chan):
    handler = SSHHandler(server, chan)
    handler.setup()
    handler.handle()
    handler.finish()


# help from:
# https://stackoverflow.com/questions/24125182/how-does-paramiko-channel-recv-exactly-work
def receive_client_data(chan):
    global command_list
    command_list = []
    command = b""
    command_count = 0

    while True:
        character = chan.recv(1024)
        if character == (b'\r' or b'\r\n' or b''):
            if command in qandr:
                chan.send("\r\n" + qandr[command])
            else:
                chan.send(b"\r\nbash: " + command + b": command not found")
            command_list.append(command)
            command_count += 1
            if command_count > 3 or command.decode("utf-8").__contains__("exit"):
                break
            command = b""
            chan.send("\r\n# ")
        else:
            command += character
            chan.send(character)
