from hpotter.plugins import *
from sqlalchemy import create_engine
from hpotter.env import logger, db
from hpotter.hpotter.HPotterDB import Base

import types
import socket
import signal

servers = []

def signal_handler(signal, frame):
    logger.info("shutting down")
    for server in servers:
        server.shutdown()


# make sure you add all non-plugins imports here
imported = ['__builtins__', 'types', 'socket', 'sqlalchemy', 'logging', \
    'signal', 'env', 'HPotterDB']

if "__main__" == __name__:

    engine = create_engine(db, echo=True)
    Base.metadata.create_all(engine)

    for name, val in list(globals().items()):
        if isinstance(val, types.ModuleType):
            if name in imported:
                continue
            for address in val.get_addresses():
                mysocket = socket.socket(address[0])

                try:
                    mysocket.bind((address[1], address[2]))
                    servers.append(val.start_server(mysocket, engine))
                except OSError as e:
                    print("bind to", address[1], address[2], e.strerror)


    signal.signal(signal.SIGINT, signal_handler)
