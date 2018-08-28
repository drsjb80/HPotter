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
                    open("/.dockerenv", "r")
                    logger.info("Running inside docker, resetting IP addresses")
                    if socket.AF_INET == address[0]:
                        IPaddress = "0.0.0.0"
                    elif socket.AF_INET6 == address[0]:
                        IPaddress = "::0"
                except:
                    IPaddress = address[1]
                    pass

                try:
                    mysocket.bind((IPaddress, address[2]))
                except OSError as e:
                    print("bind to", IPaddress, address[2], e.strerror)

                servers.append(val.start_server(mysocket, engine))

    signal.signal(signal.SIGINT, signal_handler)
