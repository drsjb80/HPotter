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


class RequestsObject(SQLAlchemyObjectType):
    id = graphene.Int()

    class Meta:
        model = Requests
