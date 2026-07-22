"""Start and stop a connection to a database, creating one if necessary."""

import os
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import database_exists, create_database

from src.tables import Base
from src.logger import logger


class Database:
    """Read from the config.yml file (if it exists) and set up the database connection."""

    def __init__(self, config):
        self.config = config
        self.lock = threading.Lock()
        self.engine = None
        self.SessionLocal = None

    def _get_database_string(self):
        """Construct database connection string from environment variables or config.

        Environment variables take precedence over config.yml:
        - DB_TYPE: database type (default: 'sqlite')
        - DB_NAME: database name (default: 'hpotter.db')
        - DB_USER: database user (for postgres)
        - DB_PASSWORD: database password (for postgres)
        - DB_HOST: database host (for postgres)
        - DB_PORT: database port (for postgres, default: 5432)
        """
        database = self.config.get('database', {})

        # Read from environment variables, fall back to config.yml
        database_type = os.environ.get('DB_TYPE', database.get('type', 'sqlite'))
        database_name = os.environ.get('DB_NAME', database.get('name', 'hpotter.db'))

        if database_type == 'sqlite':
            return f'sqlite:///{database_name}'

        database_user = os.environ.get('DB_USER', database.get('user', ''))
        database_password = os.environ.get('DB_PASSWORD', database.get('password', ''))
        database_host = os.environ.get('DB_HOST', database.get('host', ''))
        database_port = os.environ.get('DB_PORT', database.get('port', ''))

        # Some parameters are optional but must be prefixed if present
        password_part = f':{database_password}' if database_password else ''
        port_part = f':{database_port}' if database_port else ''
        name_part = f'/{database_name}' if database_name else ''

        return f'{database_type}://{database_user}{password_part}@{database_host}{port_part}{name_part}'

    def write(self, table):
        """Write into the database with a global lock."""
        with self.lock:
            session = self.SessionLocal()
            try:
                session.add(table)
                session.commit()
            finally:
                session.close()

    def open(self):
        """Open the database connection and create database if it doesn't exist."""
        logger.debug('Opening db')
        self.engine = create_engine(self._get_database_string())
        self.SessionLocal = sessionmaker(bind=self.engine)

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        Base.metadata.create_all(self.engine)

    def close(self):
        """Close the database connection."""
        logger.debug('Closing db')
        if self.engine:
            self.engine.dispose()
