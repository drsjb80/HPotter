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
    connection = graphene.Field(Connections, id=graphene.Int(), created_at=graphene.DateTime(),
                                sourceIP=graphene.String(), sourcePort=graphene.Int(),
                                destPort=graphene.Int(), proto=graphene.Int())
    connections = graphene.List(Connections)

    shell_command = graphene.Field(ShellCommands, id=graphene.Int(), command=graphene.String(),
                                   connections_id=graphene.Int())
    shell_commands = graphene.List(ShellCommands)

    http_command = graphene.Field(HTTPCommands, id=graphene.Int(), request=graphene.String(),
                                  connections_id=graphene.Int())
    http_commands = graphene.List(HTTPCommands)

    credential = graphene.Field(Credentials, id=graphene.Int(), username=graphene.String(),
                                password=graphene.String(), connections_id=graphene.Int())
    credentials = graphene.List(Credentials)

    sql_query = graphene.Field(SQL, id=graphene.Int(), request=graphene.String(), connections_id=graphene.Int())
    sql_queries = graphene.List(SQL)

    def resolve_connection(self, context, **kwargs):
        return Connections.get_query(context).filter_by(**kwargs).first()

    def resolve_connections(self, context, **kwargs):
        return Connections.get_query(info=context).all()

    def resolve_shell_command(self, context, **kwargs):
        return ShellCommands.get_query(context).filter_by(**kwargs).first()

    def resolve_shell_commands(self, context, **kwargs):
        return ShellCommands.get_query(context).all()

    def resolve_http_command(self, context, **kwargs):
        return HTTPCommands.get_query(context).filter_by(**kwargs).first()

    def resolve_http_commands(self, context, **kwargs):
        return HTTPCommands.get_query(context).all()

    def resolve_credential(self, context, **kwargs):
        return Credentials.get_query(context).filter_by(**kwargs).first()

    def resolve_credentials(self, context, **kwargs):
        return Credentials.get_query(context).all()

    def resolve_sql_query(self, context, **kwargs):
        return SQL.get_query(context).filter_by(**kwargs).first()

    def resolve_sql_queries(self, context, **kwargs):
        return SQL.get_query(context).all()


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
