import signal
import time
import argparse
import yaml

from src.logger import logger
from src import listen_thread
from src.database import Database

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
        self.config = {}
        self.database = None

    def _read_container_yaml(self, filename):
        with open(filename) as container_file:
            for container in yaml.safe_load_all(container_file):
                thread = listen_thread.listen_thread(container, self.database)
                self.listen_threads.append(thread)
                thread.start()

    def startup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', action='append', default=[])
        parser.add_argument('--container', action='append', default=[])
        args = parser.parse_args()

        self.config.update('config.yml')
        for config in args.config:
            with open(config) as config_file:
                self.config.update(yaml.safe_load(config_file))

        self.database = Database(self.config)
        self.database.open()

        self._read_container_yaml('containers.yml')
        for container in args.container:
            with open(container) as container_file:
                self._read_yaml(container_file)

    def shutdown(self):
        self.database.close()

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
