import logging
import logging.config
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

jsonserverport = 8000
