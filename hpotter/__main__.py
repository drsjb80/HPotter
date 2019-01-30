import importlib
import signal

import hpotter.plugins
from hpotter.env import logger, stop_shell

def shutdown_servers(signum, frame):
    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Stopping %s', plugin_name)
        plugin.stop_server()

    stop_shell()

    return

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
