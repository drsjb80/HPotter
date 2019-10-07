import signal

import hpotter.plugins
from hpotter.plugins.plugin_handler import start_server, stop_server, stop_all_running_containers
from hpotter.env import logger, stop_shell, close_db

plugins_dict = hpotter.plugins.__dict__

def shutdown_servers(signum, frame):
    stop_all_running_containers()
    # shell might have been started by telnet, ssh, ...
    stop_shell()
    close_db()
    
# new startup for generic plugins launcher
def startup_servers_new():
    index = 0
    for plugin_name in plugins_dict['__plugins__']:

        logger.info('Starting %s', plugin_name)
        start_server(plugin_name, index)
        index = index + 1

if "__main__" == __name__:
    signal.signal(signal.SIGTERM, shutdown_servers)
    signal.signal(signal.SIGINT, shutdown_servers)

    # startup_servers()
    startup_servers_new()
