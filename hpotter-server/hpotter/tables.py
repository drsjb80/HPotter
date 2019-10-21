from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from hpotter.env import Base, engine
from sqlalchemy.ext.declarative import declared_attr

# https://www.ietf.org/rfc/rfc1700.txt
TCP = 6
UDP = 17

# these are just initial guesses...
COMMAND_LENGTH = 4096
CREDS_LENGTH = 256


class Connections(Base):
    # pylint: disable=E0213, R0903
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    sourceIP = Column(String)
    sourcePort = Column(Integer)
    destPort = Column(Integer)
    proto = Column(Integer)


class Credentials(Base):
    # pylint: disable=E0213, R0903
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    username = Column(String(CREDS_LENGTH))
    password = Column(String(CREDS_LENGTH))
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')


class Requests(Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__tablename__.lower()

    id = Column(Integer, primary_key=True)
    request = Column(String(COMMAND_LENGTH))
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')



def check_for_tables():
    if engine.dialect.has_table(engine, 'Connections'):
        Base.prepare(engine)
        return engine.dialect.has_table
    else:
        Base.metadata.create_all(engine)


check_for_tables()
