from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
import socket
import socketserver
import threading
from datetime import *

# remember to put name in __init__.py

class HTTPTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    request = Column(String)

    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

Header = '''
HTTP/1.1 200 OK
Date: {now}
Server: Apache/2.4.6 (Red Hat Enterprise Linux) OpenSSL/1.0.2k-fips mod_fcgid/2.3.9 PHP/5.4.16
Last-Modified: {now}
Accept-Ranges: bytes
Content-Length: 1024
Cache-Control: max-age=0
{today}, Expires: {nowplustwelve}
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8

<html>
<title>Forbidden</title>
<center>
<body>
<h1>Forbidden</h1>
<p id="date"></p>
<script>
document.getElementById("date").innerHTML = Date();
</script>
</body>
</center>
</html>
'''.format(now=datetime.now(), nowplustwelve=datetime.now() + timedelta(hours=12), today=datetime.today()).encode("utf-8")

# https://hg.python.org/cpython/file/2.7/Lib/SocketServer.py

class GenericTCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def handle(self):
        data = self.request.recv(1024).decode("utf-8")

        entry = HPotterDB.HPotterDB (
            sourceIP=self.client_address[0], \
            sourcePort=self.client_address[1], \
            destIP=self.server.mysocket.getsockname()[0], \
            destPort=self.server.mysocket.getsockname()[1], \
            proto=HPotterDB.TCP)
        http = HTTPTable(request=data)
        http.hpotterdb = entry
        self.session.add(http)

        self.request.sendall(Header)

    def finish(self):
        self.session.commit()
        self.session.close()

# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class GenericServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        # save socket for use in server_bind and handler
        self.mysocket = mysocket

        # save engine for creating sessions in the handler
        self.engine = engine

        # must be called after setting mysocket as __init__ calls server_bind
        socketserver.TCPServer.__init__(self, None, GenericTCPHandler)

    def server_bind(self):
        self.socket = self.mysocket

# listen to both IPv4 and v6
def get_addresses():
    return ([(socket.AF_INET, '127.0.0.1', 8080), \
        (socket.AF_INET6, '::1', 8080)])

def start_server(my_socket, engine):
    server = GenericServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    return server
