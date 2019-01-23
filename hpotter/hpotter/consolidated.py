from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import connectiontable

class CommandTable(connectiontable.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    extend_existing=True
    id = Column(Integer, primary_key=True)
    command = Column(String)
    connectiontable_id = Column(Integer, ForeignKey('connectiontable.id'))
    connectiontable = relationship("ConnectionTable")

class LoginTable(connectiontable.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    connectiontable_id = Column(Integer, ForeignKey('connectiontable.id'))
    connectiontable = relationship("ConnectionTable")
