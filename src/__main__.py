''' The main entry point to HPotter. '''
import signal
import time
import argparse
import yaml

from src.logger import logger
from src.listen_thread import ListenThread
from src.database import Database
from src.firewall import Firewall

# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    ''' An approach to dealing with signals. '''
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # pylint: disable=W0613
    def exit_gracefully(self, signum, frame):
        ''' Called when SIGINT or SIGTERM sent to main process. '''
        logger.info('In exit_gracefully')
        self.kill_now = True

def fix_string(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

class HP():
    ''' The main class for HPotter '''
    def __init__(self):
        self.listen_threads = []
        self.config = {}
        self.database = None
        self.firewall = Firewall()

    def _read_container_yaml(self, filename):
        save = False
        with open(filename) as container_file:
            containers = list(yaml.safe_load_all(container_file))
            for container in containers:
                serial = container.get('serial', None)
                if serial:
                    serial += 1
                    container['serial'] = serial
                    save = True

                thread = ListenThread(container, self.database, self.firewall)
                self.listen_threads.append(thread)
                thread.start()

        if save:
            yaml.add_representer(str, fix_string)
            with open(filename, 'w') as container_file:
                yaml.dump_all(containers, container_file)

    def startup(self):
        ''' Read the configuration and start the listen threads. '''

        parser = argparse.ArgumentParser()
        parser.add_argument('--config', action='append',
            default=['config.yml'])
        parser.add_argument('--container', action='append',
            default=['containers.yml'])
        parser.add_argument('--loglevel', default='info',
             help='--loglevel debug|info|warning|error|critical, default=info')

        args = parser.parse_args()

        logger.setLevel(args.loglevel.upper())

        for config in args.config:
            try:
                with open(config) as config_file:
                    self.config.update(yaml.safe_load(config_file))
            except FileNotFoundError as err:
                logger.error(err)

        self.database = Database(self.config)
        self.database.open()

        self.firewall.flush()
        logger.info('creating firewall table')
        self.firewall.create_table('hpotter')

        for filename in args.container:
            self._read_container_yaml(filename)

    def shutdown(self):
        ''' Shut all the listen threads down. '''
        self.database.close()

        logger.info('Flushing firewall')
        self.firewall.flush()

        for listen_thread in self.listen_threads:
            logger.debug(listen_thread)
            if listen_thread.is_alive():
                logger.info('Calling ListenTread.shutdown')
                listen_thread.shutdown()

        for listen_thread in self.listen_threads:
            listen_thread.join()

# pylint: disable=C0122
if "__main__" == __name__: # pragma: no cover
    hp = HP()
    hp.startup()

    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(4)

    hp.shutdown()
