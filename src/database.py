"""Start and stop a connection to a database, creating one if necessary."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from src.tables import Base
from src.logger import logger


class Database:
    """Read from the config.yml file (if it exists) and set up the database connection.
    
    Each thread creates its own session via get_session() to avoid locking issues.
    """

    def __init__(self, config):
        self.config = config
        self.engine = None
        self._session_maker = None

    def _get_database_string(self):
        """Construct database connection string from config."""
        database = self.config.get('database', {})
        database_type = database.get('type', 'sqlite')
        database_name = database.get('name', 'hpotter.db')

        if database_type == 'sqlite':
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

    def get_session(self):
        """Create and return a new session for the calling thread.
        
        Each thread should call this to get its own session instance.
        
        Returns:
            A new SQLAlchemy session bound to this database.
        """
        if self._session_maker is None:
            raise RuntimeError('Database.open() must be called before get_session()')
        return self._session_maker()

    def write(self, table, session=None):
        """Write into the database.
        
        Args:
            table: The table object to write
            session: Optional session to use. If not provided, creates a new one.
        """
        should_close_session = False
        
        if session is None:
            session = self.get_session()
            should_close_session = True

        try:
            session.add(table)
            session.commit()
        finally:
            if should_close_session:
                session.close()

    def open(self):
        """Open the database connection and create database if it doesn't exist."""
        logger.debug('Opening db')
        self.engine = create_engine(self._get_database_string())

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        Base.metadata.create_all(self.engine)
        self._session_maker = sessionmaker(bind=self.engine)

    def close(self):
        """Close the database connection."""
        logger.debug('Closing db')
        if self.engine:
            self.engine.dispose()
