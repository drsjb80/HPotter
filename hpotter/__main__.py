import signal

import hpotter.plugins
from hpotter.plugins.plugin_handler import start_plugins, stop_plugins
from hpotter.env import logger, stop_shell, close_db

def shutdown_servers(signum, frame):
    stop_plugins()
    # shell might have been started by telnet, ssh, ...
    stop_shell()
    close_db()

if "__main__" == __name__:
    signal.signal(signal.SIGTERM, shutdown_servers)
    signal.signal(signal.SIGINT, shutdown_servers)

    # startup_servers()
    start_plugins()
