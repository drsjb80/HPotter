import datetime
import decimal
import json
import re
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from env import logger, db
from framework.HPotterDB import HPotterDB, Base
# fixme: find tables differently
from plugins.generic import GenericTable
from plugins.http import HTTPTable
from plugins.sh import LoginTable, CommandTable

# http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/

engine = create_engine(db, echo=True)
session = sessionmaker(bind=engine)
session = session()

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

class JSONHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print Base.metadata.tables.keys()
        url = urlparse(self.path)

        if url.path == '/':
            database = HPotterDB
        else:
            tables = Base.metadata.tables
            tableName = self.path[1:] + 'table'

            if tableName in tables.keys():
                database = tables[tableName]
            else:
                self.send_response(404)
                return

        print database

        self.send_response(200)
        self.send_header('Content-type', 'text/javascript')
        self.end_headers()

        res = session.execute(select([database]))
        dump = json.dumps([dict(r) for r in res], default=alchemyencoder)

        queries = ''
        if url.query:
            queries = parse_qs(url.query)

        if 'callback' in queries:
            self.wfile.write(queries['callback'][0] + '(')
            self.wfile.write(dump[1:-1])
            self.wfile.write(')')
        else:
            self.wfile.write(dump)

try:
    server = HTTPServer(('', 8080), JSONHandler)
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
