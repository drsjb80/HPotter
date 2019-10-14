from flask import Flask
from flask_graphql import GraphQLView

from hpotter.env import session
from hpotter.graphql.schema import schema

app = Flask(__name__)
app.debug = True

app.add_url_rule('/graphiql',
                 view_func=GraphQLView.as_view(name='GraphQL', schema=schema, grapiql=True,
                                               context={'session': session}))


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
