from hpotter.graphql.mutators import *


class Connections(SQLAlchemyObjectType):
    class Meta:
        model = Connections


class Credentials(SQLAlchemyObjectType):
    class Meta:
        model = Credentials


class Requests(SQLAlchemyObjectType):
    class Meta:
        model = Requests


class Query(graphene.ObjectType):
    connection = graphene.Field(Connections, id=graphene.Int(), created_at=graphene.DateTime(),
                                sourceIP=graphene.String(), sourcePort=graphene.Int(),
                                destPort=graphene.Int(), proto=graphene.Int())
    connections = graphene.List(Connections)

    credential = graphene.Field(Credentials, id=graphene.Int(), username=graphene.String(),
                                password=graphene.String(), connections_id=graphene.Int())
    credentials = graphene.List(Credentials)

    request = graphene.Field(Requests, id=graphene.Int(), request=graphene.String(),
                             request_type=graphene.String(), connections_id=graphene.Int())
    requests = graphene.List(Requests)

    def resolve_connection(self, context, **kwargs):
        return Connections.get_query(context).filter_by(**kwargs).first()

    def resolve_connections(self, context, **kwargs):
        return Connections.get_query(info=context).all()

    def resolve_request(self, context, **kwargs):
        return Requests.get_query(context).filter_by(**kwargs).first()

    def resolve_requests(self, context, **kwargs):
        return Requests.get_query(context).all()

    def resolve_credential(self, context, **kwargs):
        return Credentials.get_query(context).filter_by(**kwargs).first()

    def resolve_credentials(self, context, **kwargs):
        return Credentials.get_query(context).all()


class Mutations(graphene.ObjectType):
    create_connection = CreateConnection.Field()
    delete_connection = DeleteConnection.Field()
    update_connection = UpdateConnection.Field()

    create_credential = CreateCredential.Field()
    delete_credential = DeleteCredential.Field()
    update_credential = UpdateCredential.Field()

    create_request = CreateRequest.Field()
    delete_request = DeleteRequest().Field()
    update_request = UpdateRequest().Field()


schema = graphene.Schema(query=Query, mutation=Mutations)
