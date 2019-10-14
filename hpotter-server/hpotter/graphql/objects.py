import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from hpotter.tables import *


class ConnectionsObject(SQLAlchemyObjectType):
    id = graphene.Int()

    class Meta:
        model = Connections


class CredentialsObject(SQLAlchemyObjectType):
    id = graphene.Int()

    class Meta:
        model = Credentials


class ShellCommandsObject(SQLAlchemyObjectType):
    id = graphene.Int()

    class Meta:
        model = ShellCommands


class HTTPCommandsObject(SQLAlchemyObjectType):
    id = graphene.Int()

    class Meta:
        model = HTTPCommands


class SQLObject(SQLAlchemyObjectType):
    id = graphene.Int()

    class Meta:
        model = SQL
