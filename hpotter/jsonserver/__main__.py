from __future__ import print_function
import datetime
import decimal
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from hpotter.env import logger, db
from hpotter.hpotter.HPotterDB import HPotterDB, Base


# http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/

engine = create_engine(db, echo=True)
session = sessionmaker(bind=engine)
session = session()
# magic to get all the tables.
Base.metadata.reflect(bind=engine)

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

class JSONHandler(BaseHTTPRequestHandler):
    def do_HandD(self, db, res):
        self.wfile.write(b'{"header":[')
        for column in db.__table__.columns:
            self.wfile.write(b'"' + column.name.encode() + b'", ')
        self.wfile.write(b'], "data": [')
        for row in res:
            self.wfile.write(b'{')
            for column in db.__table__.columns:
                self.wfile.write(b'"' + column.name.encode() + b'" : "' + \
                    row[column.name].encode() + b'", ')
            self.wfile.write(b'} ,')
        self.wfile.write(b']}')
        
    def do_GET(self):
        url = urlparse(self.path)

        if url.path == '/':
            database = HPotterDB
        else:
            tables = Base.metadata.tables
            tableName = url.path[1:] + 'table'

            if tableName in tables.keys():
                database = tables[tableName]
            else:
                self.send_response(404)
                return

        queries = ''
        if url.query:
            queries = parse_qs(url.query)

        self.send_response(200)
        if 'callback' in queries:
            mime = 'application/javascript'
        else:
            mime = 'text/javascript'
        self.send_header('Content-type', mime)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        res = session.execute(select([database]))

        if 'handd' in queries:
            self.do_HandD(database, res)
            return

        dump = json.dumps([dict(r) for r in res], default=alchemyencoder)

        # JSONP
        if 'callback' in queries:
            self.wfile.write(queries['callback'][0].encode() + b'(')
            self.wfile.write(dump[1:-1].encode())
            self.wfile.write(b')')
        else:
            self.wfile.write(dump.encode())

try:
    server = HTTPServer(('', 8080), JSONHandler)
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
