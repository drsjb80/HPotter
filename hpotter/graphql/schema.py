from hpotter.graphql.mutators import *


class Connections(SQLAlchemyObjectType):
    class Meta:
        model = Connections


class ShellCommands(SQLAlchemyObjectType):
    class Meta:
        model = ShellCommands


class HTTPCommands(SQLAlchemyObjectType):
    class Meta:
        model = HTTPCommands


class Credentials(SQLAlchemyObjectType):
    class Meta:
        model = Credentials


class SQL(SQLAlchemyObjectType):
    class Meta:
        model = SQL


class Query(graphene.ObjectType):
    connections = graphene.List(Connections)
    shell_commands = graphene.List(ShellCommands)
    http_commands = graphene.List(HTTPCommands)
    credentials = graphene.List(Credentials)
    sql = graphene.List(SQL)

    def resolve_connections(self, context, **kwargs):
        query = Connections.get_query(context)
        return query.all()

    def resolve_shell_commands(self, context, **kwargs):
        query = ShellCommands.get_query(context)
        return query.all()

    def resolve_http_commands(self, context, **kwargs):
        query = HTTPCommands.get_query(context)
        return query.all()

    def resolve_credentials(self, context, **kwargs):
        query = Credentials.get_query(context)
        return query.all()

    def resolve_sql(self, context, **kwargs):
        query = SQL.get_query(context)
        return query.all()


class Mutations(graphene.ObjectType):
    create_connection = CreateConnection.Field()
    delete_connection = DeleteConnection.Field()
    update_connection = UpdateConnection.Field()

    create_credential = CreateCredential.Field()
    delete_credential = DeleteCredential.Field()
    update_credential = UpdateCredential.Field()

    create_shell_command = CreateShellCommand.Field()
    delete_shell_command = DeleteShellCommand().Field()
    update_shell_command = UpdateShellCommand().Field()

    create_http_command = CreateHTTPCommand.Field()
    delete_http_command = DeleteHTTPCommand().Field()
    update_http_command = UpdateHTTPCommand().Field()

    create_sql = CreateSQL.Field()
    delete_sql = DeleteSQL().Field()
    update_sql = UpdateSQL().Field()


schema = graphene.Schema(query=Query, mutation=Mutations)
