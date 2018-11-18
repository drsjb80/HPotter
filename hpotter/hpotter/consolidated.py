from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.hpotter import command_response
from paramiko.py3compat import u, decodebytes
from hpotter.docker import linux_container
import socket
import paramiko
import threading

from binascii import hexlify
import sys

# Trying to consolidate existing code as we have a lot of repeated blocks of
# code in the plugins


class CommandTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    extend_existing=True
    id = Column(Integer, primary_key=True)
    command = Column(String)
    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")

class LoginTable(HPotterDB.Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    hpotterdb_id = Column(Integer, ForeignKey('hpotterdb.id'))
    hpotterdb = relationship("HPotterDB")
