import datetime
import decimal
import json
import ipaddress

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from sqlalchemy import create_engine, func, column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from geolite2 import geolite2

from hpotter.env import db, jsonserverport
from hpotter.tables import Base, Connections, Credentials

# http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/

engine = create_engine(db) #, echo=True)
session = sessionmaker(bind=engine)
session = session()
# magic to get all the tables.
Base.metadata.reflect(bind=engine)

def minutes_ago(diff):
    return datetime.datetime.utcnow() - datetime.timedelta(minutes=diff)

def hours_ago(diff):
    return datetime.datetime.utcnow() - datetime.timedelta(hours=diff)

def days_ago(diff):
    return datetime.datetime.utcnow() - datetime.timedelta(days=diff)

def weeks_ago(diff):
    return datetime.datetime.utcnow() - datetime.timedelta(weeks=diff)

def months_ago(diff):
    # a bit of an approximation
    return weeks_ago(diff*4)

def years_ago(diff):
    return weeks_ago(diff*52)

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

    # this is for https://datatables.net/ and
    # https://github.com/daleroy1/freeboard-table
    def header_and_data(self, database, res):
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


    def geoip_header(self):
        self.wfile.write(b'{')
        self.wfile.write(b'"type": "Feature",')
        self.wfile.write(b'"geometry": {')
        self.wfile.write(b'"type": "MultiPoint",')
        self.wfile.write(b'"coordinates": [')

    def geoip_results(self, results):
        reader = geolite2.reader()
        previous = False

        for result in results:
            info = reader.get(str(result).split("'")[1])
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

    # https://tools.ietf.org/html/rfc7946#appendix-A.4
    def geoip(self):
        self.geoip_header()

        query = Connections.sourceIP
        # this order on the assumption there are fewer queries than deltas
        for delta in self.queries:
            if delta in self.deltas:
                diff = int(self.queries[delta][0])
                results = session.query(query) \
                    .filter(Connections.created_at > self.deltas[delta](diff)) \
                    .distinct()
                break
        else:
            results = session.query(query).distinct()

        self.geoip_results(results)

    def geoip_countries(self, results):
        reader = geolite2.reader()
        countries= {}

        for result in results:
            info = reader.get(str(result).split("'")[1])
            if not info:
                continue
            if "country" in info.keys():
                country = info['country']['names']['en']
                if country in countries:
                    countries[country] += 1
                else:
                    countries[country] = 1

        countries = {k:v for k,v in countries.items() if v > 5}
        country_list = []
        for k,v in countries.items():
            country_list.append({'country':k, 'count':v})

        country_list = sorted(country_list,key=lambda x: x['count'],reverse=True)
        return country_list[:10]
    
    def get_top_usernames(self):
        # this order on the assumption there are fewer queries than deltas
        labels = []
        data = []

        results = session.query(Credentials.username, func.count(Credentials.id).label('counts')) \
            .join(Connections) \
            .group_by(Credentials.username) \
            .filter(Connections.created_at > days_ago(30)) \
            .order_by('counts') \
            .all()
        
        start = max(len(results) - 10,0)
        for username, count in results[start:]:
            if count > 1:
                labels.append(username)
                data.append(count)

        self.chartjs_results("[Insert Title]", labels, data)

    def get_top_passwords(self):
        # this order on the assumption there are fewer queries than deltas
        labels = []
        data = []

        results = session.query(func.count(Credentials.id).label('counts'),Credentials.password) \
            .group_by(Credentials.username) \
            .join(Connections) \
            .filter(Connections.created_at > days_ago(30)) \
            .order_by('counts') \
            .all()
        
        start = max(len(results) - 10,0)
        for count,password in results[start:]:
            if count > 1:
                labels.append(password)
                data.append(count)

        self.chartjs_results("[Insert Title]", labels, data)

    def get_colors(self, count):
        """method to get chartjs html colors (provide number of colors)"""
        default_colors = ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850", "#c39bd3", "#85c1e9", " #d35400", "#7dcea0", "#f1c40f"]
        if count > len(default_colors):
            default_colors = default_colors*(count // len(default_colors) + 1)
        return default_colors[:count]    

    def chartjs_results(self, title, labels, data):
        # TODO pass in labels, data
        colors = self.get_colors(len(labels))

        self.wfile.write(b'{"data": {')
        self.wfile.write('"labels": {},'.format(json.dumps(labels)).encode())
        self.wfile.write(b'"datasets": {')
        self.wfile.write('"label": "{}",'.format(title).encode())
        self.wfile.write('"backgroundColor": {},'.format(json.dumps(colors)).encode())
        self.wfile.write('"data": {}'.format(data).encode()) 
        self.wfile.write(b'}}}')

    def chartjs(self, query):
        query = Connections.sourceIP
        # this order on the assumption there are fewer queries than deltas
        results = session.query(query) \
            .filter(Connections.created_at > days_ago(30)) \
            .distinct()
        labels = []
        data = []
        countries = self.geoip_countries(results)
        for country_count in countries:
            labels.append(country_count['country'])
            data.append(country_count['count'])
        self.chartjs_results("[Insert Title]", labels, data)
    
    def get_daily_attacks(self):
        results = session.query(func.count(Connections.id).label('counts'), Connections.created_at) \
            .group_by(func.date(Connections.created_at)) \
            .all()
        labels = []
        data = []
        for count,date in results:
            if count > 1:
                labels.append(str(date.date()))
                data.append(count)

        self.chartjs_results("Title", labels, data)

    def send_headers(self):
        self.send_response(200)
        if 'callback' in self.queries:
            mime = 'application/javascript'
        else:
            mime = 'text/javascript'
        self.send_header('Content-type', mime)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # pylint: disable=C0103
    def do_GET(self):
        url = urlparse(self.path)
        if url.path.endswith('.html'):
            SimpleHTTPRequestHandler.do_GET(self)
            return

        tables = Base.metadata.tables
        table_name = url.path[1:]

        if table_name in tables.keys():
            database = tables[table_name]
        else:
            self.send_response(404)
            return

        # here, so as not to override __init__
        # pylint: disable=W0201
        self.queries = {}
        if url.query:
            self.queries = parse_qs(url.query)

        self.send_headers()

        # here, so as not to override __init__
        # pylint: disable=W0201
        self.deltas = { \
            'minutes_ago':  minutes_ago, \
            'hours_ago':    hours_ago, \
            'days_ago':     days_ago, \
            'weeks_ago':    weeks_ago, \
            'months_ago':   months_ago, \
            'years_ago':    years_ago \
        }

        if table_name == 'connections' and 'geoip' in self.queries:
            self.geoip()
            return
        elif 'chartjs' in self.queries:
            self.chartjs(table_name)
            return
        elif 'passwords' in self.queries:
            self.get_top_passwords()
            return
        elif 'usernames' in self.queries:
            self.get_top_usernames()
            return
        elif 'attacks' in self.queries:
            self.get_daily_attacks()
            return

        query = select([database])

        for delta in self.deltas:
            if delta in self.queries:
                diff = int(self.queries[delta][0])
                query = session.query(database).join(Connections) \
                    .filter(Connections.created_at > self.deltas[delta](diff))
                break

        results = session.execute(query)

        if 'handd' in self.queries:
            self.header_and_data(database, results)
            return

        dump = json.dumps([dict(r) for r in results], default=alchemyencoder)

        # JSONP
        if 'callback' in self.queries:
            self.wfile.write(self.queries['callback'][0].encode() + b'(')
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
