''' The schema for storing HPotter data in a RDBMS.'''

from sqlalchemy import Column, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy_utils import IPAddressType

# https://www.ietf.org/rfc/rfc1700.txt
TCP = 6
UDP = 17

Base = declarative_base()

class Connections(Base):
    ''' The schema for all connections made to HPotter '''
    # pylint: disable=E0213, R0903, E1101
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    sourceIP = Column(IPAddressType)
    sourcePort = Column(Integer)
    destIP = Column(IPAddressType)
    destPort = Column(Integer)
    proto = Column(Integer)

class Credentials(Base):
    ''' Store username and passwords where appropriate. '''
    # pylint: disable=E0213, R0903, E1101
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')

class Data(Base):
    ''' The requests (and possibly responses) to/from HPotter containers.  '''
    # pylint: disable=E0213, R0903, E1101
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    direction = Column(Text)
    data = Column(Text)
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')
