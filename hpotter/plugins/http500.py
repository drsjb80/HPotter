from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import connectiontable
from hpotter.env import logger, Session
from datetime import *

import socket
import socketserver
import threading

# remember to put name in __init__.py

class HTTPTable(connectiontable.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    request = Column(String)

    connectiontable_id = Column(Integer, ForeignKey('connectiontable.id'))
    connectiontable = relationship("ConnectionTable")


Header = '''
HTTP/1.0 500 Internal Server Error
Date: {now}
Server: Apache/2.4.6 (Red Hat Enterprise Linux) OpenSSL/1.0.2k-fips mod_fcgid/2.3.9 PHP/5.4.16
Last-Modified: {now}
Cache-Control: max-age=0
Content-Type: text/html; charset=UTF-8

<html>
<head>
<title>500 Internal Server Error</title>
</head>
<body>
500 Internal Server Error
</body>
</html>
'''.format(now=datetime.now())

class HTTPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.session = Session()
        data = self.request.recv(4096).decode("utf-8")

        entry = connectiontable.ConnectionTable(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.server_address[0],
            destPort=self.server.server_address[1],
            proto=connectiontable.TCP)
        http = HTTPTable(request=data)
        http.connectiontable = entry
        self.session.add(http)
        self.session.commit()
        Session.remove()

        self.request.sendall(Header.encode('utf-8'))

class HTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

def start_server():
    server = HTTPServer(('0.0.0.0', 80), HTTPHandler)
    server.serve_forever()

def stop_server():
    pass
