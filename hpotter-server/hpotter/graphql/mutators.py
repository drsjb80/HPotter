from hpotter.env import session
from hpotter.graphql.objects import *
from hpotter.tables import *
from datetime import datetime


class CreateConnection(graphene.Mutation):
    class Input:
        created_at = graphene.DateTime()
        sourceIP = graphene.String()
        sourcePort = graphene.Int()
        destPort = graphene.Int()
        proto = graphene.Int()

    connection = graphene.Field(lambda: ConnectionsObject)

    def mutate(self, info, **args):
        connection = Connections(**args)
        session.add(connection)
        session.commit()
        return CreateConnection(connection=connection)


class DeleteConnection(graphene.Mutation):
    class Input:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, **args):
        session.query(Connections).filter(Connections.id == args['id']).delete()
        session.commit()
        return DeleteConnection(ok=True)


class UpdateConnection(graphene.Mutation):
    class Input:
        id = graphene.Int(required=True)
        # created_at = graphene.DateTime()
        sourceIP = graphene.String()
        sourcePort = graphene.Int()
        destPort = graphene.Int()
        proto = graphene.Int()

    connection = graphene.Field(lambda: ConnectionsObject)

    def mutate(self, info, **args):
        connection = Connections(**args)
        keys = args.keys()
        if 'sourceIP' in keys:
            session.query(Connections).filter(Connections.id == args['id']). \
                update({Connections.sourceIP: args['sourceIP']})
        if 'sourcePort' in keys:
            session.query(Connections).filter(Connections.id == args['id']). \
                update({Connections.sourcePort: args['sourcePort']})
        if 'destPort' in keys:
            session.query(Connections).filter(Connections.id == args['id']). \
                update({Connections.destPort: args['destPort']})
        if 'proto' in keys:
            session.query(Connections).filter(Connections.id == args['id']). \
                update({Connections.proto: args['proto']})
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
        session.query(Connections).filter(Connections.id == args['id']).update({Connections.created_at: time})
        session.commit()
        return UpdateConnection(connection=connection)


class CreateCredential(graphene.Mutation):
    class Input:
        username = graphene.String(CREDS_LENGTH)
        password = graphene.String(CREDS_LENGTH)
        connections_id = graphene.Int()

    credential = graphene.Field(lambda: CredentialsObject)

    def mutate(self, info, **args):
        credential = Credentials(**args)
        session.add(credential)
        session.commit()
        return CreateCredential(credential=credential)


class DeleteCredential(graphene.Mutation):
    class Input:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, **args):
        session.query(Credentials).filter(Credentials.id == args['id']).delete()
        session.commit()
        return DeleteCredential(ok=True)


class UpdateCredential(graphene.Mutation):
    class Input:
        id = graphene.Int()
        username = graphene.String(CREDS_LENGTH)
        password = graphene.String(CREDS_LENGTH)
        connections_id = graphene.Int()

    credential = graphene.Field(lambda: CredentialsObject)

    def mutate(self, info, **args):
        credential = Credentials(**args)
        keys = args.keys()
        if 'username' in keys:
            session.query(Credentials).filter(Credentials.id == args['id']).\
                update({Credentials.username: args['username']})
        if 'password' in keys:
            session.query(Credentials).filter(Credentials.id == args['id']). \
                update({Credentials.password: args['password']})
        if 'connections_id' in keys:
            session.query(Credentials).filter(Credentials.id == args['id']). \
                update({Credentials.connections_id: args['connections_id']})
        session.commit()
        return UpdateCredential(credential=credential)


class CreateRequest(graphene.Mutation):
    class Input:
        request = graphene.String(COMMAND_LENGTH)
        request_type = graphene.String(REQUEST_TYPE_LENGTH)
        connections_id = graphene.Int()

    request = graphene.Field(lambda: RequestsObject)

    def mutate(self, info, **args):
        shell_command = Requests(**args)
        session.add(shell_command)
        session.commit()
        return CreateRequest(request=shell_command)


class DeleteRequest(graphene.Mutation):
    class Input:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, **args):
        session.query(Requests).filter(Requests.id == args['id']).delete()
        session.commit()
        return DeleteRequest(ok=True)


class UpdateRequest(graphene.Mutation):
    class Input:
        id = graphene.Int()
        request = graphene.String(COMMAND_LENGTH)
        request_type = graphene.String(REQUEST_TYPE_LENGTH)
        connections_id = graphene.Int()

    request = graphene.Field(lambda: RequestsObject)

    def mutate(self, info, **args):
        request = Requests(**args)
        keys = args.keys()
        if 'request' in keys:
            session.query(Requests).filter(Requests.id == args['id']).\
                update({Requests.request: args['request']})
        if 'request_type' in keys:
            session.query(Requests).filter(Requests.id == args['id']).\
                update({Requests.request_type: args['request_type']})
        if 'connections_id' in keys:
            session.query(Requests).filter(Requests.id == args['id']). \
                update({Requests.connections_id: args['connections_id']})
        session.commit()
        return UpdateRequest(request=request)
