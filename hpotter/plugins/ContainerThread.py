import socket
import threading
import docker
import time

from hpotter.env import logger
from hpotter.plugins.OneWayThread import OneWayThread

class ContainerThread(threading.Thread):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.dest = self.thread1 = self.thread2 = self.container = None

    def connect_to_container(self):
        IPAddress = self.container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
        logger.debug(IPAddress)

        ports = self.container.attrs['NetworkSettings']['Ports']

        if len(ports) != 1:
            logger.info('throw a fit')

        port = None
        for p in ports.keys():
            port = int(p.split('/')[0])
        logger.debug(port)

        for x in range(9):
            try:
                self.dest = socket.create_connection((IPAddress, port), timeout=2)
                break
            except OSError as err:
                if err.errno == 111:
                    time.sleep(2)
                    continue
                logger.info('Unable to connect to ' + IPAddress + ':' + str(port))
                logger.info(err)
                raise err

    def run(self):
        try:
            client = docker.from_env()
            self.container = client.containers.run('httpd:latest', detach=True)
            self.container.reload()
        except Exception as err:
            logger.info(err)
            return

        try:
            self.connect_to_container()
        except Exception as err:
            logger.info(err)
            self.stop_and_remove()
            return

        try:
            self.dest.sendall(b'GET / HTTP/1.0\r\n\r\n')
            data = self.dest.recv(1024)
            logger.info(data)
            self.dest.close()
        except Exception as err:
            logger.info(err)
            return

        '''
        self.thread1 = OneWayThread(self.source, self.dest)
        self.thread1.start()
        self.thread2 = OneWayThread(self.dest, self.source)
        self.thread2.start()

        self.shutdown()
        '''

        self.stop_and_remove()

    def shutdown(self):
        logger.info('Joining thread1')
        self.thread1.join()
        logger.info('Joining thread2')
        self.thread2.join()

        self.dest.close()

        self.stop_and_remove()

    def stop_and_remove(self):
        logger.debug(str(self.container.logs()))
        logger.info('Stopping: %s', self.container)
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()

    def stop_container():
        # send request along to both OneWayPipes...
        shutdown()

