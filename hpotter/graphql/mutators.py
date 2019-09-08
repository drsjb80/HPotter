from hpotter.env import session
from hpotter.graphql.objects import *
from hpotter.tables import *


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
        created_at = graphene.DateTime()
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


class CreateShellCommand(graphene.Mutation):
    class Input:
        command = graphene.String(SHELL_COMMAND_LENGTH)
        connections_id = graphene.Int()

    shell_command = graphene.Field(lambda: ShellCommandsObject)

    def mutate(self, info, **args):
        shell_command = ShellCommands(**args)
        session.add(shell_command)
        session.commit()
        return CreateShellCommand(shell_command=shell_command)


class DeleteShellCommand(graphene.Mutation):
    class Input:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, **args):
        session.query(ShellCommands).filter(ShellCommands.id == args['id']).delete()
        session.commit()
        return DeleteShellCommand(ok=True)


class UpdateShellCommand(graphene.Mutation):
    class Input:
        id = graphene.Int()
        command = graphene.String(SHELL_COMMAND_LENGTH)
        connections_id = graphene.Int()

    shell_command = graphene.Field(lambda: ShellCommandsObject)

    def mutate(self, info, **args):
        shell_command = ShellCommands(**args)
        keys = args.keys()
        if 'command' in keys:
            session.query(ShellCommands).filter(ShellCommands.id == args['id']).\
                update({ShellCommands.command: args['command']})
        if 'connections_id' in keys:
            session.query(ShellCommands).filter(ShellCommands.id == args['id']). \
                update({ShellCommands.connections_id: args['connections_id']})
        session.commit()
        return UpdateShellCommand(shell_command=shell_command)


class CreateHTTPCommand(graphene.Mutation):
    class Input:
        request = graphene.String(HTTP_COMMAND_LENGTH)
        connections_id = graphene.Int()

    http_command = graphene.Field(lambda: HTTPCommandsObject)

    def mutate(self, info, **args):
        http_command = HTTPCommands(**args)
        session.add(http_command)
        session.commit()
        return CreateHTTPCommand(http_command=http_command)


class DeleteHTTPCommand(graphene.Mutation):
    class Input:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, **args):
        session.query(HTTPCommands).filter(HTTPCommands.id == args['id']).delete()
        session.commit()
        return DeleteHTTPCommand(ok=True)


class UpdateHTTPCommand(graphene.Mutation):
    class Input:
        id = graphene.Int()
        request = graphene.String(HTTP_COMMAND_LENGTH)
        connections_id = graphene.Int()

    http_command = graphene.Field(lambda: HTTPCommandsObject)

    def mutate(self, info, **args):
        http_command = HTTPCommands(**args)
        keys = args.keys()
        if 'request' in keys:
            session.query(HTTPCommands).filter(HTTPCommands.id == args['id']).\
                update({HTTPCommands.request: args['request']})
        if 'connections_id' in keys:
            session.query(HTTPCommands).filter(HTTPCommands.id == args['id']). \
                update({HTTPCommands.connections_id: args['connections_id']})
        session.commit()
        return UpdateHTTPCommand(http_command=http_command)


class CreateSQL(graphene.Mutation):
    class Input:
        request = graphene.String(SQL_COMMAND_LENGTH)
        connections_id = graphene.Int()

    sql_command = graphene.Field(lambda: SQLObject)

    def mutate(self, info, **args):
        sql_command = SQL(**args)
        session.add(sql_command)
        session.commit()
        return CreateSQL(sql_command=sql_command)


class DeleteSQL(graphene.Mutation):
    class Input:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, **args):
        session.query(SQL).filter(SQL.id == args['id']).delete()
        session.commit()
        return DeleteSQL(ok=True)


class UpdateSQL(graphene.Mutation):
    class Input:
        id = graphene.Int()
        request = graphene.String(SQL_COMMAND_LENGTH)
        connections_id = graphene.Int()

    sql = graphene.Field(lambda: SQLObject)

    def mutate(self, info, **args):
        sql = SQL(**args)
        keys = args.keys()
        if 'request' in keys:
            session.query(SQL).filter(SQL.id == args['id']).\
                update({SQL.request: args['request']})
        if 'connections_id' in keys:
            session.query(SQL).filter(SQL.id == args['id']). \
                update({SQL.connections_id: args['connections_id']})
        session.commit()
        return UpdateSQL(sql=sql)
