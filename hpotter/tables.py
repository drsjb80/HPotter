from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from hpotter.env import Base, engine
from sqlalchemy.ext.declarative import declared_attr

# https://www.ietf.org/rfc/rfc1700.txt
TCP = 6
UDP = 17

# these are just initial guesses...
SHELL_COMMAND_LENGTH = 512
HTTP_COMMAND_LENGTH = 4096
SQL_COMMAND_LENGTH = 512
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


class ShellCommands(Base):
    # pylint: disable=E0213, R0903
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    command = Column(String(SHELL_COMMAND_LENGTH))
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')


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


class HTTPCommands(Base):
    # pylint: disable=E0213, R0903
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    request = Column(String(HTTP_COMMAND_LENGTH))
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')


class SQL(Base):
    # pylint: disable=E0213, R0903
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    request = Column(String(SQL_COMMAND_LENGTH))
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')


def checkForTables():
    #checks for one table, if this table exists it is assumed that all tables exist
    if engine.dialect.has_table(engine, 'Connections'):
        Base.prepare(engine)
        return(engine.dialect.has_table)
    else:
        Base.metadata.create_all(engine)

checkForTables()
