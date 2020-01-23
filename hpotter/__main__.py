import sys
import signal
import time
import yaml

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

listen_threads = []

def startup():
    # open_db()
    global listen_threads

    with open('plugins.yaml') as f:
        for data in yaml.safe_load_all(f):
            lt = ListenThread(data)
            listen_threads.append(lt)
            lt.start()

def shutdown():
    # close_db()
    logger.info('In shutdown')
    for lt in listen_threads:
        if lt.is_alive():
            lt.shutdown()

if "__main__" == __name__:
    startup()

    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(5)

    shutdown()
