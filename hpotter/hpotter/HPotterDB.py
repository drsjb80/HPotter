from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy_utils import IPAddressType
from sqlalchemy import Column, Integer, DateTime, func

# https://www.ietf.org/rfc/rfc1700.txt
TCP = 6
UDP = 17
SSH = 88

Base = declarative_base()

class HPotterDB(Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    sourceIP = Column(IPAddressType)
    sourcePort = Column(Integer)
    destIP = Column(IPAddressType)
    destPort = Column(Integer)
    proto = Column(Integer)
