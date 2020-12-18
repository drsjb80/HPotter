import sys
import signal
import time
import yaml
import argparse

from src.logger import logger
from src import ListenThread
from src.database import database

# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info('In exit_gracefully')
        self.kill_now = True

class HP():
    def __init__(self):
        self.listen_threads = []

    def read_yaml(self, filename):
        try:
            with open(filename) as f:
                for config in yaml.safe_load_all(f):
                    lt = ListenThread.ListenThread(config)
                    self.listen_threads.append(lt)
                    lt.start()
        except FileNotFoundError as fnfe:
            logger.info(fnfe)

    def startup(self):
        database.open()

        self.read_yaml('config.yml')

        parser = argparse.ArgumentParser()
        parser.add_argument('--p', action='append', default=[])
        args = parser.parse_args()

        for arg in args.p:
            self.read_yaml(arg)

    def shutdown(self):
        database.close()

        for lt in self.listen_threads:
            logger.debug(lt)
            if lt.is_alive():
                logger.info('Calling ListenTread.shutdown')
                lt.shutdown()

if "__main__" == __name__:
    hp = HP()
    hp.startup()

    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(5)

    hp.shutdown()
