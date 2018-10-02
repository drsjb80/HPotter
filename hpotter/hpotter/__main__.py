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
    # global t

    for val in list(globals().items()):
        print(val)

    engine = create_engine(db, echo=True)
    Base.metadata.create_all(engine)

    # Currently, first if isinstance is evaluating ssh and ssl,
    # So when it gets to the second one, it tries going again.
    # This leave the ssh/ssl plugin incapable of handling its channel,
    # As it can never escape these if commands.
    # All plugins will start because they are in the first iteration
    # maybe try this?

    # instead of:
    # global t
    # replace with:
    # t = ssl.handle_client(ssl.my_socket)
    # then down below:
    # start_server(my_socket, engine, t)
    for name, val in list(globals().items()):
        if isinstance(val, types.ModuleType):
            if (name in imported) and (name != ("ssh" or "ssl")):
                continue
            for address in val.get_addresses():
                mysocket = socket.socket(address[0])

                try:
                    mysocket.bind((address[1], address[2]))
                    servers.append(val.start_server(mysocket, engine))
                except OSError as e:
                    print("bind to", address[1], address[2], e.strerror)

        # maybe remove this instance to be outside of the for loop
        # that way, all plugins will be activated
        # then this one will be taken care of lastly, as we have to
        # wait for a client to connect...
        # Also, will allow for the removal of t, as
        # we don't have to worry about waiting for the other
        # plugins anymore.
        if isinstance(val, types.ModuleType):
            if name in imported == "ssh" or "ssl":
                continue
            for address in val.get_addresses():
                mysocket = socket.socket(address[0])

                try:
                    mysocket.bind((address[1], address[2]))
                    server, t = val.start_server(mysocket, engine, t)
                    servers.append(server)
                    print()
                except OSError as e:
                    print("bind to", address[1], address[2], e.strerror)

    signal.signal(signal.SIGINT, signal_handler)

    # change with other changes
    if "ssh" or "ssl" in imported:
        ssl.handle_channel(t)
