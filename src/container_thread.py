''' Starts a container and connects two one-way threads to it. Called from
a listening thread. '''

from ast import literal_eval
import socket
import threading
import time
import docker
import os
# import psutil
import platform

from src.logger import logger
from src.one_way_thread import OneWayThread
from src.lazy_init import lazy_init

class ContainerThread(threading.Thread):
    ''' The thread that gets created in listen_thread. '''
    # pylint: disable=E1101, W0613
    @lazy_init
    def __init__(self, source, connection, container_config, database):
        super().__init__()
        self.container_ip = self.container_port = self.container_protocol = None
        self.dest = self.thread1 = self.thread2 = self.container = None

    def _connect_to_container(self):
        nwsettings = self.container.attrs['NetworkSettings']
        ports = nwsettings['Ports']
        assert len(ports) == 1

        if platform.system() == 'Linux':
            self.container_ip = nwsettings['Networks']['bridge']['IPAddress']

        for port in ports.keys():
            self.container_protocol = port.split('/')[1]

            if platform.system() == 'Linux':
                self.container_port = int(port.split('/')[0])
            elif platform.system() == 'Darwin':
                # for MacOS, while there is a 172 address assigned to
                # containers, one can't connect to it easily. instead, we
                # publish all and look for the localhost port.
                self.container_ip=ports[port][0]['HostIp']
                self.container_port=ports[port][0]['HostPort']

        logger.debug(self.container_ip)
        logger.debug(self.container_protocol)
        logger.debug(self.container_port)

        for _ in range(9):
            try:
                self.dest = socket.create_connection( \
                    (self.container_ip, self.container_port), timeout=2)
                self.dest.settimeout(self.container_config.get('connection_timeout', 10))
                logger.debug("Opening %s", self.dest)
                return
            except Exception as err:
                logger.debug(err)
                time.sleep(2)

        logger.info('Unable to connect to %s: %s', self.container_ip, str(self.container_port))


    def _start_and_join_threads(self):
        logger.debug('Starting thread1')
        self.thread1 = OneWayThread(self.source, self.dest, self.connection,
            self.container_config, 'request', self.database)
        self.thread1.start()

        logger.debug('Starting thread2')
        self.thread2 = OneWayThread(self.dest, self.source, self.connection,
            self.container_config, 'response', self.database)
        self.thread2.start()

        logger.debug('Joining thread1')
        self.thread1.join()
        logger.debug('Joining thread2')
        self.thread2.join()

        logger.debug("Closing %s", self.source)
        self.source.close()
        logger.debug("Closing %s", self.dest)
        self.dest.close()

    def run(self):
        try:
            # logger.debug(psutil.Process().num_fds())
            client = docker.from_env()
            logger.debug("created %s", client)
            if platform.system() == 'Darwin':
                self.container = \
                    client.containers.run(self.container_config['container'], \
                    **literal_eval(
                        self.container_config.get(
                            "arguments",
                            '{"publish_all_ports":True, "detach":True}'
                        )
                    ))
            else:
                self.container = \
                    client.containers.run(self.container_config['container'], \
                    **literal_eval(
                        self.container_config.get(
                            "arguments",
                            '{"detach":True}'
                        )
                    ))
            logger.info('Started: %s', self.container)
            self.container.reload()
        except Exception as err:
            logger.info(err)
            logger.debug("Closing %s", client)
            client.close()
            return

        try:
            # logger.debug(psutil.Process().num_fds())
            self._connect_to_container()
            # logger.debug(psutil.Process().num_fds())
        except Exception as err:
            logger.info(err)
            self._stop_and_remove()
            return

        self._start_and_join_threads()
        self._stop_and_remove()

        # https://github.com/docker/docker-py/issues/2766
        # this apparently has to come after the containers are stopped in
        # order to correctly remove the fds.
        logger.debug("Closing %s", client)
        # logger.debug(psutil.Process().num_fds())
        client.close()
        # logger.debug(psutil.Process().num_fds())

    def _stop_and_remove(self):
        logger.debug(str(self.container.logs()))
        logger.info('Stopping: %s', self.container)
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()

    def shutdown(self):
        ''' Called to shutdown the one-way threads and stop and remove the
        container. Called externally in response to a shutdown request. '''
        self.thread1.shutdown()
        self.thread2.shutdown()
        self.dest.close()
        self._stop_and_remove()
