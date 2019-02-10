import datetime
import decimal
import json
import ipaddress

import os
import geoip2.database
import _geoip_geolite2

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from hpotter.env import logger, db, jsonserverport
from hpotter.tables import Connections, Base

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


class JSONHandler(BaseHTTPRequestHandler):
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
        
    def geoip(self, results):
        # https://tools.ietf.org/html/rfc7946#appendix-A.4

        city_table = os.path.join(os.path.dirname(_geoip_geolite2.__file__), \
            _geoip_geolite2.database_name)
        reader = geoip2.database.Reader(city_table)

        self.wfile.write(b'{')
        self.wfile.write(b'"type": "Feature",')
        self.wfile.write(b'"geometry": {')
        self.wfile.write(b'"type": "MultiPoint",')
        self.wfile.write(b'"coordinates": [')

        previous = False
        for result in results:


            try:
                location = reader.city(str(result.sourceIP)).location

                if previous:
                    self.wfile.write(b',')
                previous = True

                self.wfile.write(b'[')
                self.wfile.write(str(location.longitude).encode())
                self.wfile.write(b',')
                self.wfile.write(str(location.latitude).encode())
                self.wfile.write(b']')
            except geoip2.errors.AddressNotFoundError:
                # print('no location')
                previous = False

        self.wfile.write(b']}}')

    # pylint: disable=C0103
    def do_GET(self):
        url = urlparse(self.path)
        # print(url)

        tables = Base.metadata.tables
        table_name = url.path[1:] + 'table'

        if table_name in tables.keys():
            database = tables[table_name]
        else:
            self.send_response(404)
            return

        queries = ''
        if url.query:
            queries = parse_qs(url.query)
            # print(queries)

        self.send_response(200)
        if 'callback' in queries:
            mime = 'application/javascript'
        else:
            mime = 'text/javascript'
        self.send_header('Content-type', mime)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        results = session.execute(select([database]))
        
        if table_name == 'connectiontable' and 'geoip' in queries:
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
    print('^C received, shutting down the web server')
    server.socket.close()
