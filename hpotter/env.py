import os
import sys
import logging
import logging.config
import platform
import threading
import docker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database
from hpotter.tables import Base

logging.config.fileConfig('hpotter/logging.conf')
logger = logging.getLogger('hpotter')

DB=os.getenv('HPOTTER_DB', 'sqlite')
DB_USER=os.getenv('HPOTTER_DB_USER', 'root')
DB_PASSWORD=os.getenv('HPOTTER_DB_PASSWORD', '')
DB_HOST=os.getenv('HPOTTER_DB_HOST', '127.0.0.1')
DB_PORT=os.getenv('HPOTTER_DB_PORT', '')
DB_DB=os.getenv('HPOTTER_DB_DB', 'hpotter')

db = None
if DB != 'sqlite':
    if DB_PASSWORD:
        DB_PASSWORD = ':' + DB_PASSWORD

    if DB_PORT:
        DB_PORT = ':' + DB_PORT

    if DB_DB:
        DB_DB = '/' + DB_DB

    db = '{0}://{1}{2}@{3}{4}{5}'.format(DB, DB_USER, DB_PASSWORD, \
        DB_HOST, DB_PORT, DB_DB)
    logger.debug(db)

    def write_db(table):
        session.add(table)
        session.commit()
else:
    db = 'sqlite:///main.db'

    db_lock = threading.Lock()
    def write_db(table):
        with db_lock:
            session.add(table)
            session.commit()

engine = create_engine(db)
# engine = create_engine(db, echo=True)

# https://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(engine))()

def close_db():
    logger.info('Closing db')
    session.commit()
    session.close()
    logger.info('Done closing db')

# a start, for a Pi 0.
machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''

busybox = True
shell_container = None

# i can't figure out why i can get logger in shell.py but not shell_container
def get_shell_container():
    return shell_container

def start_shell():
    global shell_container
    if shell_container:
        logger.info('Shell container already started')
        return

    logger.info('Starting shell container')
    client = docker.from_env()
    if busybox:
        shell_container = client.containers.run(machine + 'busybox:latest', \
            command=['/bin/ash'], tty=True, detach=True, read_only=True)
    else:
        shell_container = client.containers.run(machine + 'alpine:latest', \
            command=['/bin/ash'], user='guest', tty=True, detach=True, \
                read_only=True)

    logger.debug(shell_container)

    client.networks.get('bridge').disconnect(shell_container)

def stop_shell():
    if not shell_container:
        return

    logger.info('Stopping shell container')
    logger.debug(shell_container)
    shell_container.stop()
    logger.info('Removing shell container')
    shell_container.remove()

jsonserverport = 8000

# some singletons
telnet_server = None
http500_server = None
ssh_server_thread = None
