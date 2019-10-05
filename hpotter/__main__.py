import signal

import hpotter.plugins
from hpotter.plugins.plugin_handler import start_server, stop_server, stop_all_running_containers
from hpotter.env import logger, stop_shell, close_db

plugins_dict = hpotter.plugins.__dict__

def shutdown_servers(signum, frame):
    '''
    for plugin_name in plugins_dict['__shell__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Stopping %s', plugin_name)
        plugin.stop_server()
        logger.info('Done stopping %s', plugin_name)
    '''
    # for plugin_name in plugins_dict['__shutdown__']:
    #     logger.info('Stopping %s', plugin_name)
    #     stop_server(plugin_name)
    #     logger.info('Done stopping %s', plugin_name)

    stop_all_running_containers()
    # shell might have been started by telnet, ssh, ...
    stop_shell()
    close_db()

'''
def startup_servers():
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Starting %s', plugin_name)
        plugin.start_server()
'''
# new startup for generic plugins launcher
def startup_servers_new():
    index = 0
    for plugin_name in plugins_dict['__plugins__']:

        logger.info('Starting %s', plugin_name)
        start_server(plugin_name, index)
        index = index + 1
'''
    for plugin_name in plugins_dict['__shell__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Starting %s', plugin_name)
        plugin.start_server()

def shutdown_servers(signum, frame):
    for plugin_name in plugin_dict['__plugin__']:
        #importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Stopping %s', plugin_name)
        plugin.stop_server()
        logger.info('Done stopping %s', plugin_name)

    for plugin_name in plugin_dict['__shell__']:
        importlib.import_module('hpotter.plugin.' plugin_name)
        plugin = plugin_dict[plugin_name]
        logger.info('Stopping %s', plugin_name)
        plugin.stop_server()
        logger.info('Done stopping %s', plugin_name)
'''


if "__main__" == __name__:
    signal.signal(signal.SIGTERM, shutdown_servers)
    signal.signal(signal.SIGINT, shutdown_servers)

    # startup_servers()
    startup_servers_new()
