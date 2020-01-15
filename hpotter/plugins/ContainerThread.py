import socket
import threading
import docker

from hpotter.env import logger
from hpotter.plugins.OneWayThread import OneWayThread

class ContainerThread(threading.Thread):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.dest = self.thread1 = self.thread2 = self.container = None
        self.network = self.IPAddress = None

    def run(self):
        try:
            client = docker.from_env()
            self.container = client.containers.run( \
                'httpd:latest', \
                detach=True)
            logger.info('Created: %s', self.container)
        except Exception as err:
            logger.info(err)
            return

        '''
        try:
            self.network = client.networks.create('httpipe', driver='bridge')
            logger.info('Created: %s', self.network)
        except Exception as err:
            logger.info(err)
            self.stopAndRemove()
            return
        '''

        '''
        try:
            self.network.connect(self.container)
            self.network.reload()
            logger.info(self.network.containers)
        except Exception as err:
            logger.info(err)
            self.stopAndRemove()
            return
        '''

        try:
            self.container.reload()
            logger.info(self.container.attrs['NetworkSettings']['Networks'])
            self.IPAddress = self.container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
            logger.info('Connecting to (' + self.IPAddress + ', 8080)');
            self.dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dest.settimeout(30)
            self.dest.connect((self.IPAddress, 8080))
            logger.debug(str(self.dest))
        except Exception as err:
            logger.info(err)
            self.stopAndRemove()
            return

        self.thread1 = OneWayThread(self.source, self.dest)
        self.thread1.start()
        self.thread2 = OneWayThread(self.dest, self.source)
        self.thread2.start()

        self.shutdown()

    def shutdown(self):
        logger.info('Joining thread1')
        self.thread1.join()
        logger.info('Joining thread2')
        self.thread2.join()

        self.dest.close()

        self.stopAndRemove()

    def stopAndRemove(self):
        logger.debug(str(self.container.logs()))
        logger.info('Stopping: %s', self.container)
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()

    def stop_container():
        # send request along to both OneWayPipes...
        shutdown()

