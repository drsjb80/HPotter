from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from plugins.generic import GenericTable
from framework.HPotterDB import HPotterDB
from env import logger, db
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer 
import json
import decimal, datetime

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
        print self.path
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        res = session.execute(select([HPotterDB]))
        self.wfile.write(json.dumps([dict(r) for r in res],
            default=alchemyencoder))

try:
	server = HTTPServer(('', 8000), JSONHandler)
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
