import importlib
import signal
import threading

import hpotter.plugins
from hpotter.env import logger, stop_shell

def shutdown_servers(signum, frame):
    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Stopping %s', plugin_name)
        plugin.stop_server()
        logger.info('Done stopping %s', plugin_name)

    # shell might have been started by telnet, ssh, ...
    stop_shell()

def startup_servers():
    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Starting %s', plugin_name)
        plugin.start_server()

if "__main__" == __name__:
    signal.signal(signal.SIGINT, shutdown_servers)

    startup_servers()
