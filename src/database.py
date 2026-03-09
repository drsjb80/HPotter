"""Start and stop a connection to a database, creating one if necessary."""

import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database

from src.tables import Base
from src.logger import logger

db_thread_lock = threading.Lock()


class Database:
    """Read from the config.yml file (if it exists) and set up the database connection."""

    def __init__(self, config):
        self.config = config
        self.lock_needed = False
        self.engine = None

    def _get_database_string(self):
        """Construct database connection string from config."""
        database = self.config.get('database', {})
        database_type = database.get('type', 'sqlite')
        database_name = database.get('name', 'hpotter.db')

        if database_type == 'sqlite':
            self.lock_needed = True
            return f'sqlite:///{database_name}'

        database_user = database.get('user', '')
        database_password = database.get('password', '')
        database_host = database.get('host', '')
        database_port = database.get('port', '')

        # Some parameters are optional but must be prefixed if present
        password_part = f':{database_password}' if database_password else ''
        port_part = f':{database_port}' if database_port else ''
        name_part = f'/{database_name}' if database_name else ''

        return f'{database_type}://{database_user}{password_part}@{database_host}{port_part}{name_part}'

    def write(self, table):
        """Write into the database, with locking if necessary."""
        session = scoped_session(sessionmaker(self.engine))()

        def _commit_and_close():
            session.add(table)
            session.commit()
            session.close()

        if self.lock_needed:
            with db_thread_lock:
                _commit_and_close()
        else:
            _commit_and_close()

    def open(self):
        """Open the database connection and create database if it doesn't exist."""
        logger.debug('Opening db')
        self.engine = create_engine(self._get_database_string())

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        Base.metadata.create_all(self.engine)

    def close(self):
        """Close the database connection."""
        logger.debug('Closing db')
