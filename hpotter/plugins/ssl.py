from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from datetime import datetime
import socket
import paramiko
import ssl
import socketserver
import threading
from paramiko.py3compat import u, decodebytes
from binascii import hexlify
import sys

host_key = paramiko.RSAKey(filename="RSAKey.cfg")

print("Read key: " + u(hexlify(host_key.get_fingerprint())))

# put all the simple text queries in here
# later, create file that text queries are pulled from
# list will be long and used by ssl, ssh, and telnet
qandr = {b'ls': 'foo\n',
         b'more': 'bar\n'}


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


class SSLHandler(socketserver.BaseRequestHandler):
    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def handle(self):
        entry = HPotterDB.HPotterDB(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.mysocket.getsockname()[0],
            destPort=self.server.mysocket.getsockname()[1],
            proto=HPotterDB.TCP)

        # Asks for username and password
        self.request.sendall(b'Username: ')
        username = self.request.recv(1024).strip().decode("utf-8")
        self.request.sendall(b'Password: ')
        password = self.request.recv(1024).strip().decode("utf-8")

        login = LoginTable(username=username, password=password)
        login.hpotterdb = entry
        self.session.add(login)

        # Controls what is printed to output line when the user accesses the ssl plugin
        # Same rules apply to the telnet plugin as of now
        self.request.sendall(b'Last login: Whatever you want it to be\n')
        self.request.sendall(b'# ')

        command = self.request.recv(1024).strip()

        cmd = CommandTable(command=command.decode("utf-8"))
        cmd.hpotterdb = entry
        self.session.add(cmd)

        if command in qandr:
            self.request.sendall(qandr[command].encode("utf-8"))
        elif command == b"date":
            date = datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")
            self.request.sendall(date.encode("utf-8") + b'\n')
        else:
            # default response to commands not found in qandr list
            self.request.sendall(b'bash: ' + command + b': command not found\n')

    def finish(self):
        self.session.commit()
        self.session.close()


# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class SSLServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        # save socket for use in server_bind and handler
        self.mysocket = mysocket

        # save engine for creating sessions in the handler
        self.engine = engine

        # must be called after setting mysocket as __init__ calls server_bind
        socketserver.TCPServer.__init__(self, None, SSLHandler)

    def server_bind(self):
        self.socket = self.mysocket


# listen to both IPv4 and v6
def get_addresses():
    return ([(socket.AF_INET, '127.0.0.1', 22),
             (socket.AF_INET6, '::1', 22)])


# ssh necessities
class SSHWrapper(paramiko.ServerInterface):
    # 'data' is the output of base64.b64encode(key)
    # (using the "user_rsa_key" files
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    allow_reuse_address = True

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    # Checks the username and password, returning statements based on success/failure -JN
    def check_auth_password(self, username, password):
        if(username == "user") and (password == "root"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    # Checks for username & key
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

    # Turned off gssapi authentication because I couldn't get it to work properly
    def enable_auth_gssapi(self):
        return False
        # return True

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
            self, channel, term, width, height, pixelwidth, pixelheight,
            modes):
        return True


# Need to figure out how to create a certchain.pem
# Also, how to SSL into the honeypot (if possible)
# Maybe use this same approach when using Paramiko for SSH
# If not, see if SSL can be used as an SSH wrapper
def start_server(my_socket, engine):
    t = handle_client(my_socket)
    t.load_server_moduli()
    t.add_server_key(host_key)
    server = SSLServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print("server started")
    return server, t


def handle_client(my_socket):
    my_socket.listen(100)
    print("Waiting for connection...")
    client, addr = my_socket.accept()
    t = paramiko.Transport(client)
    return t


def handle_channel(t):
    chan = t.accept(20)
    if chan is None:
        print("*** No channel.")
        sys.exit(1)
    print("You're in!")

    chan.send("\r\n I think it worked")
    print("closing channel")
    chan.close()
