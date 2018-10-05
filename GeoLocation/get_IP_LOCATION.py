import re
import json
from urllib2 import urlopen

url = 'http://ipinfo.io/json/'
response = urlopen(url)
data = json.load(response)

ip=data['ip']
org=data['org']
city=data['city']
country=data['country']
region=data['region']
location=data['loc']

print 'Location of incomming request:\n '
print 'IP : {4} \nRegion : {1} \nCountry : {2} \nCity : {3} \nOrg : {0}'.format(org,region,country,city,ip)

# Seperate location string
for lat, lon in (pair.split(',') for pair in location.split()):
    print "Latitude : ", lat, "\nLongitude : ", lon
