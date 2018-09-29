from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from datetime import datetime
import socket
import ssl
import socketserver
import threading

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
    return ([(socket.AF_INET, '127.0.0.1', 8443),
        (socket.AF_INET6, '::1', 8443)])


# Need to figure out how to create a certchain.pem
# Also, how to SSL into the honeypot (if possible)
# Maybe use this same approach when using Paramiko for SSH
# If not, see if SSL can be used as an SSH wrapper
def start_server(my_socket, engine):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('/path/to/certchain.pem', 'private.key')
    with context.wrap_socket(my_socket, server_side=True) as ssock:
        conn, addr = ssock.accept()
    server = SSLServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    return server
