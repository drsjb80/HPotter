import datetime
import decimal
import json
import ipaddress

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from geolite2 import geolite2

from hpotter.env import logger, db, jsonserverport
from hpotter.tables import Base

# http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/

engine = create_engine(db) #, echo=True)
session = sessionmaker(bind=engine)
session = session()
# magic to get all the tables.
Base.metadata.reflect(bind=engine)

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
        return float(obj)

    if isinstance(obj, ipaddress.IPv4Address):
        return str(obj)

    if isinstance(obj, ipaddress.IPv6Address):
        return str(obj)

class JSONHandler(SimpleHTTPRequestHandler):
    # this is for https://datatables.net/ and https://github.com/daleroy1/freeboard-table
    def hander_and_data(self, database, res):
        self.wfile.write(b'{"header":[')
        for column in database.__table__.columns:
            self.wfile.write(b'"' + column.name.encode() + b'", ')
        self.wfile.write(b'], "data": [')
        for row in res:
            self.wfile.write(b'{')
            for column in database.__table__.columns:
                self.wfile.write(b'"' + column.name.encode() + b'" : "' + \
                    str(row[column.name]).encode() + b'", ')
            self.wfile.write(b'} ,')
        self.wfile.write(b']}')

    # https://tools.ietf.org/html/rfc7946#appendix-A.4
    def geoip(self, results):
        reader = geolite2.reader()

        self.wfile.write(b'{')
        self.wfile.write(b'"type": "Feature",')
        self.wfile.write(b'"geometry": {')
        self.wfile.write(b'"type": "MultiPoint",')
        self.wfile.write(b'"coordinates": [')

        previous = False
        for result in results:
            info = reader.get(str(result.sourceIP))
            if not info:
                continue

            location = info['location']
            if not location:
                continue

            if previous:
                self.wfile.write(b',')
            previous = True

            self.wfile.write(b'[')
            self.wfile.write(str(location['longitude']).encode())
            self.wfile.write(b',')
            self.wfile.write(str(location['latitude']).encode())
            self.wfile.write(b']')

        self.wfile.write(b']}}')

    # pylint: disable=C0103
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/simplemap.html':
            SimpleHTTPRequestHandler.do_GET(self)
            return

        tables = Base.metadata.tables
        table_name = url.path[1:]

        if table_name in tables.keys():
            database = tables[table_name]
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

        results = session.execute(select([database]))

        if table_name == 'connections' and 'geoip' in queries:
            self.geoip(results)
            return

        if 'handd' in queries:
            self.hander_and_data(database, results)
            return

        dump = json.dumps([dict(r) for r in results], default=alchemyencoder)

        # JSONP
        if 'callback' in queries:
            self.wfile.write(queries['callback'][0].encode() + b'(')
            self.wfile.write(dump[1:-1].encode())
            self.wfile.write(b')')
        else:
            self.wfile.write(dump.encode())

try:
    server = HTTPServer(('', jsonserverport), JSONHandler)
    server.serve_forever()

except KeyboardInterrupt:
    print('Shutting down the web server')
    server.socket.close()
