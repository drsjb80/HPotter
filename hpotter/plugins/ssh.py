from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
<<<<<<< HEAD
import socket
import socketserver
import paramiko
import threading
import sys
import traceback
from paramiko.py3compat import u, decodebytes
from binascii import hexlify


# remember to put name in __init__.py

# https://docs.python.org/3/library/socketserver.html

# Help from: https://github.com/paramiko/paramiko/blob/master/demos/demo_server.py

host_key = paramiko.RSAKey(filename="RSAKey.cfg")

print("Read key: " + u(hexlify(host_key.get_fingerprint())))


class SSHTable(HPotterDB.Base):
=======
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
>>>>>>> dev
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
<<<<<<< HEAD
    request = Column(String)
=======
    username = Column(String)
    password = Column(String)
>>>>>>> dev

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")


<<<<<<< HEAD
class SSHHandler(socketserver.BaseRequestHandler):
=======
class SSHHandler:
    def __init__(self, server, chan):
        self.server = server
        self.chan = chan

>>>>>>> dev
    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def handle(self):
<<<<<<< HEAD
        data = self.request.recv(1024)

        entry = HPotterDB.HPotterDB(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.mysocket.getsockname()[0],
            destPort=self.server.mysocket.getsockname()[1],
            proto=HPotterDB.TCP)
        ssh = SSHTable(request=data)
        ssh.hpotterdb = entry
        self.session.add(ssh)
=======
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
>>>>>>> dev

    def finish(self):
        self.session.commit()
        self.session.close()

<<<<<<< HEAD
# class SSHServer(socketserver.ThreadingMixIn):
#     allow_reuse_address = True
#
#     def __init__(self, mysocket):
#         self.mysocket = mysocket
#
#     def server_bind(self):
#         self.socket = self.mysocket


class SSHServer(socketserver.ThreadingMixIn, paramiko.ServerInterface):
    # 'data' is the output of base64.b64encode(key)
    # (using the "user_rsa_key" files
=======

class SSHServer(socketserver.ThreadingMixIn, socketserver.TCPServer, paramiko.ServerInterface):
>>>>>>> dev
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))
<<<<<<< HEAD
    # good_pub_key = host_key

    allow_reuse_address = True

    def __init__(self, mysocket):
        self.event = threading.Event()
        self.mysocket = mysocket

    def server_bind(self):
        self.socket = self.mysocket
=======

    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        self.mysocket = mysocket
        self.engine = engine
        socketserver.TCPServer.__init__(self, None, None)
        self.event = threading.Event()
>>>>>>> dev

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

<<<<<<< HEAD
    # Checks the username and password, returning statements based on success/failure -JN
    def check_auth_password(self, username, password):
        if(username == "user") and (password == "root"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    # Checks for username & key
    # key should be the good_pub_key from above
    # If not, change in freeSSH -JN
=======
    def check_auth_password(self, username, password):
        global attack_username, attack_password
        attack_username, attack_password = username, password
        # changed so that any username/password can be used
        if username and password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

>>>>>>> dev
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

<<<<<<< HEAD
    def check_auth_gssapi_keyex(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file = None):
=======
    def check_auth_gssapi_keyex(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None):
>>>>>>> dev
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

<<<<<<< HEAD
    # Turned off gssapi authentication because I couldn't get it to work properly
    # Will look into at a later date -JN
    def enable_auth_gssapi(self):
        return False
        # return True
=======
    # Turned off, causing problems
    def enable_auth_gssapi(self):
        return False
>>>>>>> dev

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
            self, channel, term, width, height, pixelwidth, pixelheight,
            modes):
        return True

<<<<<<< HEAD

DoGSSAPIKeyExchange = True
=======
    def server_bind(self):
        self.socket = self.mysocket
>>>>>>> dev


# listen to both IPv4 and v6
def get_addresses():
<<<<<<< HEAD
    return ([(socket.AF_INET, '127.0.0.1', 88),
        (socket.AF_INET6, '::1', 88)])


# def start_server(my_socket, engine):
#     t = paramiko.Transport(my_socket)
#     t.load_server_moduli()
#     t.add_server_key(host_key)
#     server = SSHServer(my_socket, engine)
#     t.start_server(server=server)
#     print("Server started")
#     return server


# now connect
def start_server(my_socket, engine):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", 88))
    except Exception as e:
        print("*** Bind failed: " + str(e))
        traceback.print_exc()
        sys.exit(1)

    try:
        sock.listen(100)
        print("Listening for connection ...")
        client, addr = sock.accept()
    except Exception as e:
        print("*** Listen/accept failed: " + str(e))
        traceback.print_exc()
        sys.exit(1)

    print("Got a connection!")

    try:
        t = paramiko.Transport(client)
        # t = paramiko.Transport(client, gss_kex=DoGSSAPIKeyExchange)
        # t.set_gss_host(socket.getfqdn(""))
        # Can't get to work, commented for now -JN
        try:
            t.load_server_moduli()
        except:
            print("(Failed to load moduli -- gex will be unsupported.)")
            raise
        t.add_server_key(host_key)
        server = SSHServer(my_socket)
        try:
            t.start_server(server=server)
            print("Server started")
        except paramiko.SSHException:
            print("*** SSH negotiation failed.")
            sys.exit(1)

        # wait for auth
        chan = t.accept(20)
        if chan is None:
            print("*** No channel.")
            sys.exit(1)
        print("Authenticated!")

        server.event.wait(10)
        if not server.event.is_set():
            print("*** Client never asked for a shell.")
            sys.exit(1)

        # Can be removed or manipulated at a later date
        # All from git documentation for tests - JN
        chan.send("\r\n\rWelcome to my dorky little BBS!\r\n\r\n")
        chan.send(
            "We are on fire all the time! Hooray! Candy corn for everyone!\r\n"
        )
        chan.send("Happy birthday to Robot Dave!\r\n\r\n")
        chan.send("Username: ")
        f = chan.makefile("rU")
        username = f.readline().strip("\r\n")
        chan.send("\r\nI don't like you, " + username + ".\r\n")
        chan.close()

    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        t.close()
        #try:
        #    t.close()
        #except Exception as e:
        #    pass
=======
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
>>>>>>> dev
