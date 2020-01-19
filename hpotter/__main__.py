import sys
import signal
import time

from hpotter.plugins.ListenThread import ListenThread
from hpotter.env import logger, open_db, close_db

# plugins_dict = hpotter.plugins.__dict__

# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info('In exit_gracefully')
        self.kill_now = True

listenThread = None

def shutdown_servers():
    # close_db()
    logger.info('In shutdown_servers')
    listenThread.request_shutdown()

def startup_servers():
    # open_db()
    global listenThread
    listenThread = ListenThread(('127.0.0.1', 8080))
    listenThread.start()

if "__main__" == __name__:
    startup_servers()

    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(5)

    shutdown_servers()
