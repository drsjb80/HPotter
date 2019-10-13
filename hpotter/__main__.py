import signal, sys, inspect, os

import hpotter.plugins
from hpotter.plugins.plugin_handler import start_plugins, stop_plugins
from hpotter.env import logger, stop_shell, close_db

def shutdown_servers(signum, frame):
    stop_plugins()
    # shell might have been started by telnet, ssh, ...
    stop_shell()
    close_db()

def shutdown_win_servers(signum):
    stop_plugins()
    # shell might have been started by telnet, ssh, ...
    stop_shell()
    close_db()

if sys.platform != 'win32':
    if "__main__" == __name__:
      signal.signal(signal.SIGTERM, shutdown_servers)
      signal.signal(signal.SIGINT, shutdown_servers)
    start_plugins()
else:
    if "__main__" == __name__:
       import win32api
       win32api.SetConsoleCtrlHandler(shutdown_win_servers)

    # startup_servers()
    start_plugins()
