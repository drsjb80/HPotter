import logging
import logging.config
import platform
import docker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from hpotter.hpotter.HPotterDB import Base

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

busybox=True
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

jsonserverport = 8000
