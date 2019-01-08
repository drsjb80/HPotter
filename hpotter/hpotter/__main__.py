import hpotter.plugins
import importlib

from sqlalchemy import create_engine
from hpotter.env import logger, db
from hpotter.hpotter.HPotterDB import Base
from hpotter.docker import linux_container

import socket
import signal

def shutdown_servers(signum, frame):
    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        plugin.stop_server()

if "__main__" == __name__:
    signal.signal(signal.SIGINT, shutdown_servers)

    # fire up the db
    engine = create_engine(db, echo=True)
    Base.metadata.create_all(engine)

    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        for address in plugin.get_addresses():
            mysocket = socket.socket(address[0])
            try:
                mysocket.bind((address[1], address[2]))
                plugin.start_server(mysocket, engine)
            except OSError as e:
                print("bind to", address[1], address[2], e.strerror)
