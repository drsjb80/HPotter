import logging
import logging.config
import platform
import docker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from hpotter.hpotter.connectiontable import Base

logging.config.fileConfig('hpotter/logging.conf')
logger = logging.getLogger('hpotter')

# note sqlite:///:memory: can't be used, even for testing, as it
# doesn't work with threads.
db = 'sqlite:///main.db'
engine = create_engine(db, echo=True)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(engine))

# a start, for a Pi 0.
machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''

busybox = True
shell_container = None

def startShell():
    global shell_container
    if shell_container:
        return

    client = docker.from_env()
    if busybox:
        shell_container = client.containers.run(machine + 'busybox', 
            command=['/bin/ash'], tty=True, detach=True, read_only=True)
    else:
        shell_container = client.containers.run(machine + 'alpine',
            command=['/bin/ash'], user='guest', tty=True, detach=True,
            read_only=True)

    network = client.networks.get('bridge')
    network.disconnect(shell_container)

def stopShell():
    if not shell_container:
        return
    shell_container.stop()
    shell_container.remove()

jsonserverport = 8000
