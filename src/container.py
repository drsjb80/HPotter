'''Starts a container and connects two one-way threads to it. Called from
a listening thread.'''

import socket
import time
import docker

from src.logger import logger
from src.one_way_thread import OneWayThread
from src.lazy_init import lazy_init


class Container:
    '''Handler invoked by listen_thread.'''
    # pylint: disable=W0613
    @lazy_init
    def __init__(self, source, connection, container_config, database):
        # This is a plain object with a ``run`` method which the executor will call.
        self.container_ip = self.container_port = self.container_protocol = None
        self.dest = self.thread1 = self.thread2 = self.container = None

    def _connect_to_container(self):
        nwsettings = self.container.attrs['NetworkSettings']
        self.container_ip = nwsettings['Networks']['bridge']['IPAddress']
        logger.debug(nwsettings)
        logger.debug(self.container_ip)

        ports = nwsettings['Ports']
        assert len(ports) == 1

        for port in ports.keys():
            self.container_port = int(port.split('/')[0])
            self.container_protocol = port.split('/')[1]
        logger.debug(self.container_port)
        logger.debug(self.container_protocol)

        # try 10 times as we might not connect the first time
        for _ in range(9):
            try:
                logger.debug("Attempting to open %s %s", self.container_ip, self.container_port)
                self.dest = socket.create_connection(
                    (self.container_ip, self.container_port), timeout=2)
                self.dest.settimeout(self.container_config.get('socket_timeout', 10))
                return
            except Exception as err:
                logger.debug({err})
                time.sleep(2)

        raise ConnectionError('Unable to connect to container')

    def _start_and_join_threads(self):
        try:
            logger.debug('Starting thread1')
            self.thread1 = OneWayThread(
                self.source, self.dest, self.connection,
                self.container_config, 'request', self.database)
            self.thread1.start()

            logger.debug('Starting thread2')
            self.thread2 = OneWayThread(
                self.dest, self.source, self.connection,
                self.container_config, 'response', self.database)
            self.thread2.start()

            # Wait for both to finish
            self.thread1.join()
            self.thread2.join()
        finally:
            logger.debug("Closing %s", self.source)
            try:
                self.source.close()
            except Exception as err:
                logger.debug("Error closing source socket: %s", err)
            logger.debug("Closing %s", self.dest)
            try:
                self.dest.close()
            except Exception as err:
                logger.debug("Error closing dest socket: %s", err)

    def run(self):
        client = None
        try:
            client = docker.from_env()
            logger.debug("created %s", client)
            self.container = client.containers.run(self.container_config['container'], detach=True)
            logger.info('Started: %s', self.container)
            self.container.reload()

            self._connect_to_container()
            self._start_and_join_threads()
            self._stop_and_remove()
        except Exception as err:
            logger.warning('Error in container thread: %s', err)
            # Only attempt cleanup if we have a container
            if hasattr(self, 'container') and self.container:
                try:
                    self._stop_and_remove()
                except Exception as cleanup_err:
                    logger.debug('Error during cleanup: %s', cleanup_err)
        finally:
            if client:
                try:
                    logger.debug("Closing %s", client)
                    client.close()
                except Exception as close_err:
                    logger.debug('Error closing docker client: %s', close_err)

    def _stop_and_remove(self):
        logger.debug(str(self.container.logs()))
        logger.info('Stopping: %s', self.container)
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()

    def shutdown(self):
        '''Shut down the one-way threads and stop and remove the container.'''
        if hasattr(self, 'thread1') and self.thread1:
            self.thread1.shutdown()
        if hasattr(self, 'thread2') and self.thread2:
            self.thread2.shutdown()
        if hasattr(self, 'container') and self.container:
            try:
                self._stop_and_remove()
            except Exception as err:
                logger.error('Error during shutdown cleanup: %s', err)
        if hasattr(self, 'dest') and self.dest:
            try:
                self.dest.close()
            except Exception as err:
                logger.debug('Error closing dest socket during shutdown: %s', err)
