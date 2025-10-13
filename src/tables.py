"""Database schema for storing HPotter honeypot data.

This module defines SQLAlchemy ORM models for storing connection data,
credentials captured by honeypots, and request/response data.

Protocol constants are based on IANA protocol numbers:
https://www.ietf.org/rfc/rfc1700.txt
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy_utils import IPAddressType

# IANA protocol numbers
TCP = 6
UDP = 17

Base = declarative_base()

# Note: SQLite doesn't support Numeric types well for lat/long
# For more precision with other databases, consider:
# latitude = Column(Numeric(8, 6))
# longitude = Column(Numeric(9, 6))
# Reference: https://stackoverflow.com/questions/1196415/

class Connections(Base):
    """Database model for connection records.

    Stores information about each connection attempt to the honeypot,
    including source/destination details and geolocation data.

    Attributes:
        id: Primary key
        created_at: Timestamp when connection was established
        source_address: IP address of the connecting client
        source_port: Port number used by the client
        destination_address: IP address of the honeypot listener
        destination_port: Port number of the honeypot listener
        latitude: Geographic latitude of source IP (string format)
        longitude: Geographic longitude of source IP (string format)
        container: Name of the honeypot container that handled this connection
        proto: Protocol number (TCP=6, UDP=17)
    """

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name (lowercase)."""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    source_address = Column(IPAddressType)
    source_port = Column(Integer)
    destination_address = Column(IPAddressType)
    destination_port = Column(Integer)
    latitude = Column(Text)
    longitude = Column(Text)
    container = Column(Text)
    proto = Column(Integer)

class Credentials(Base):
    """Database model for captured credentials.

    Stores usernames and passwords captured from authentication attempts
    to honeypot services (SSH, FTP, Telnet, etc.).

    Attributes:
        id: Primary key
        username: Username attempted by the attacker
        password: Password attempted by the attacker
        connections_id: Foreign key to the Connections table
        connection: Relationship to the associated Connections record
    """

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name (lowercase)."""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')

class Data(Base):
    """Database model for request/response data.

    Stores the actual data exchanged between clients and honeypot containers,
    including both requests from attackers and responses from honeypots.

    Attributes:
        id: Primary key
        direction: Data flow direction ('request' or 'response')
        data: The actual data content (string representation of bytes)
        connections_id: Foreign key to the Connections table
        connection: Relationship to the associated Connections record
    """

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name (lowercase)."""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    direction = Column(Text)
    data = Column(Text)
    connections_id = Column(Integer, ForeignKey('connections.id'))
    connection = relationship('Connections')
