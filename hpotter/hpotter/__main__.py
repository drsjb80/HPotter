from hpotter.plugins import *
from sqlalchemy import create_engine
from hpotter.env import logger, db
from hpotter.hpotter.HPotterDB import Base
from hpotter.ubuntu import ubuntu_container

import types
import socket
import signal

# make sure you add all non-plugins imports here
imported = ['__builtins__', 'types', 'socket', 'sqlalchemy', 'logging',
            'signal', 'env', 'HPotterDB', 'ubuntu_container']

<<<<<<< HEAD

def start_ssh_server(engine):
    global transport

    for name, val in list(globals().items()):
        if name.__contains__('ssh'):
            if isinstance(val, types.ModuleType):
                if name in imported:
                    continue
                for address in val.get_addresses():
                    mysocket = socket.socket(address[0])

                    try:
                        mysocket.bind((address[1], address[2]))
                        server, transport = val.start_server(mysocket, engine)
                        servers.append(server)
                        ssh.channel_handler(transport, server, mysocket)
                    except OSError as e:
                        print("bind to", address[1], address[2], e.strerror)


def start_servers():
    global local_engine
    local_engine = create_engine(db, echo=True)
    Base.metadata.create_all(local_engine)
=======
if "__main__" == __name__:
    # fire up the db
    engine = create_engine(db, echo=True)
    Base.metadata.create_all(engine)
>>>>>>> dev

    for name, val in list(globals().items()):
        if name in imported:
            continue
        if isinstance(val, types.ModuleType):
            for address in val.get_addresses():
                mysocket = socket.socket(address[0])

                try:
                    mysocket.bind((address[1], address[2]))
<<<<<<< HEAD
                    servers.append(val.start_server(mysocket, local_engine))
                except OSError as e:
                    print("bind to", address[1], address[2], e.strerror)


if "__main__" == __name__:

    start_servers()
    ubuntu_container.check_docker_version()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    start_ssh_server(local_engine)
=======
                    val.start_server(mysocket, engine)
                except OSError as e:
                    print("bind to", address[1], address[2], e.strerror)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
>>>>>>> dev
