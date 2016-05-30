from plugins import *
import types
import socket
from sqlalchemy import create_engine
import logging
import env

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.warning("starting main")

# make sure you add all non-plugins imports here
imported = ['__builtins__', 'types', 'socket', 'sqlalchemy', 'logging', 'env']

if "__main__" == __name__:

    # note sqlite:///:memory: can't be used, even for testing, as it 
    # doesn't work with threads.
    engine = create_engine('sqlite:///main.db', echo=True)

    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            if name in imported:
                continue
            for address in val.get_addresses():
                mysocket = socket.socket()
                mysocket.bind(address)
                val.start_server(mysocket, engine, None)
                print("after start_server")
