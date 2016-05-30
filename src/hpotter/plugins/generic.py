import socket
import socketserver
# import logging
# import env
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler())
# logger.info("starting generic")

Base = declarative_base()

class GenericTable(Base):
    __tablename__ = 'generic'

    id = Column(Integer, primary_key=True)
    echo = Column(String)
    source_address = Column(String)
    source_port = Column(Integer)

class GenericTCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        Session = sessionmaker(bind=self.server.engine)
        self.session = Session()

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))

        self.session.add(GenericTable(echo=self.data, \
            source_address=self.client_address[0], \
            source_port=self.client_address[1]))

        self.request.sendall(self.data.upper())

    def finish(self):
        self.session.commit()
        self.session.close()

# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class GenericServer(socketserver.ThreadingTCPServer):
    def __init__(self, mysocket, engine):
        # save socket for use in server_bind
        self.mysocket = mysocket

        # save engine for creating sessions in the handler
        self.engine = engine

        socketserver.TCPServer.__init__(self, None, GenericTCPHandler)

    def server_bind(self):
        # print('in server_bind')
        self.socket = self.mysocket

def get_addresses():
    return ([('127.0.0.1', 2000)])

def start_server(socket, engine, logger):
    Base.metadata.create_all(engine)
    GenericServer(socket, engine).serve_forever()
