from mpl_toolkits.basemap import Basemap
from urllib.request import urlopen
import matplotlib.pyplot as plt
import json
import sqlite3

# NOTE: Change root for main.db before running

# Folium imports
# import numpy as np


def globe(ip_list):

    # size of window
    plt.figure(figsize=(50, 24))
    
    map = Basemap(projection='robin', lat_0=0, lon_0=0)
    # map = Basemap(projection='ortho',lat_0=45,lon_0=-100,resolution='l')
    # map = Basemap(projection='ortho', resolution='l', lat_0=50, lon_0=0)

    # draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth=0.30)
    map.drawcountries(linewidth=0.30)
    map.drawstates(linewidth=0.30)
    # map.fillcontinents(color='dimgray',lake_color='darkgray')
    # map.fillcontinents(color='coral',lake_color='aqua')

    map.bluemarble()
    # draw the edge of the map projection region (the projection limb)
    map.drawmapboundary(fill_color='darkgray')

    # draw lat/lon grid lines every 30 degrees.
    # map.drawmeridians(np.arange(0,360,30))
    # map.drawparallels(np.arange(-90,90,30))

    local_ipv4, local_ipv6, ex_denver_ip= "127.0.0.1", "::1", "174.16.111.55"
    previous_ip = []  # Prevents re-iterating through ip's already plotted
    for ip in ip_list:
        if ip in previous_ip:
            continue
        if ip == local_ipv4 or local_ipv6:
            lat, lon = get_ip(ex_denver_ip)
        else:
            lat, lon = get_ip(ip)
        previous_ip.append(ip)
        x, y = map(lon, lat)
        map.plot(x, y, "ro")

    plt.title("Incoming IP Address").set_fontsize(50)
    plt.show()


def get_ip(ip):
    latitude, longitude = "", ""
    url = "http://ipinfo.io/{ip}".format(ip=ip)
    response = urlopen(url)
    data = json.load(response)
    print(data)
    ip = data['ip']
    org = data['org']
    city = data['city']
    country = data['country']
    region = data['region']
    location = data['loc']

    #  I can comment this out and return one answer...  this will work better
    for lat, lon in (pair.split(',') for pair in location.split()):
        latitude = lat
        longitude = lon
        # print("Latitude : ", lat, "\nLongitude : ", lon)
        
    return latitude, longitude    


def connect():

    bag_of_ips = []

    # Change path for your machine's main.db location, starting at the top level (Windows: C:/, E:/ F:/, etc.)
    sqlite_db = 'F:/Hugh Mungus/Documents/hpotter/HPotter/main.db'
    table_name = 'hpotterdb'
    column1 = 'id'
    column2 = 'sourceIP'
    sql = "SELECT {col2} FROM {tn};". format(col2=column2, tn=table_name)
    # Connect to db
    conn = sqlite3.connect(sqlite_db)
    c = conn.cursor()

    c.execute(sql)
    
    answer = c.fetchall()
    
    for x in answer:
        # print(x[0])
        bag_of_ips.append(x[0])

    # print(bag_of_ips)

    globe(bag_of_ips)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    connect()

