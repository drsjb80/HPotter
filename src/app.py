'''Core application logic for HPotter.'''
import argparse
import signal
import threading
import yaml

from src.logger import logger
from src.listen_thread import ListenThread
from src.database import Database
from src.metrics import METRICS_ENABLED, start_http_server


class GracefulKiller:
    '''An approach to dealing with signals.'''
    def __init__(self, shutdown_event):
        self.shutdown_event = shutdown_event
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # pylint: disable=W0613
    def exit_gracefully(self, signum, frame):
        '''Called when SIGINT or SIGTERM are sent to the process.'''
        logger.info('In exit_gracefully')
        self.shutdown_event.set()


def fix_string(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")


class HP():
    '''The main class for HPotter.'''
    def __init__(self):
        self.listen_threads = []
        self.config = {}
        self.database = None

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

                thread = ListenThread(container, self.database)
                self.listen_threads.append(thread)
                thread.start()

        if save:
            yaml.add_representer(str, fix_string)
            with open(filename, 'w') as container_file:
                yaml.dump_all(containers, container_file)

    def startup(self, args):
        '''Read the configuration and start the listen threads.'''
        logger.setLevel(args.loglevel.upper())

        for config in args.config:
            try:
                with open(config) as config_file:
                    self.config.update(yaml.safe_load(config_file))
            except FileNotFoundError as err:
                logger.error(err)

        self.database = Database(self.config)
        self.database.open()

        if METRICS_ENABLED:
            try:
                start_http_server(8000)
                logger.info('Prometheus metrics available on port 8000')
            except Exception as exc:
                logger.error('Failed to start Prometheus HTTP server: %s', exc)
        else:
            logger.info('prometheus_client not installed; Prometheus metrics disabled')

        for filename in args.container:
            self._read_container_yaml(filename)

    def shutdown(self):
        '''Shut all the listen threads down.'''
        if self.database:
            self.database.close()

        for listen_thread in self.listen_threads:
            logger.debug(listen_thread)
            if listen_thread.is_alive():
                logger.info('Calling ListenTread.shutdown')
                listen_thread.shutdown()

        for listen_thread in self.listen_threads:
            listen_thread.join()


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', action='append', default=['config.yml'])
    parser.add_argument('--container', action='append', default=['containers.yml'])
    parser.add_argument('--loglevel', default='info',
                        help='--loglevel debug|info|warning|error|critical, default=info')
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    hp = HP()
    try:
        hp.startup(args)

        shutdown_event = threading.Event()
        GracefulKiller(shutdown_event)
        logger.info('Waiting for SIGINT/SIGTERM')
        shutdown_event.wait()
    finally:
        hp.shutdown()
