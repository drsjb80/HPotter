import socket
import threading

from hpotter import tables
from hpotter.env import logger, write_db

# remember to put name in __init__.py

class ContainerThread(threading.Thread):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.dest = self.thread1 = self.thread2 = self.container = None

    def run(self):
        try:
            client = docker.from_env()
            self.container = client.containers.run( \
                'httpd:latest', \
                detach=True, \
                ports={'80/tcp': 8080})
            logger.info('Created: %s', self.container)
        except Exception as err:
            logger.info(err)
            return

        try:
            self.dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dest.settimeout(30)
            self.dest.connect(('127.0.0.1', 8080))
        except Exception as err:
            logger.info(err)
            return

        self.thread1 = OneWayThread(self.source, self.dest).start()
        self.thread2 = OneWayThread(self.dest, self.source).start()
        shutdown()

    def shutdown()
        logger.info('Joining thread1')
        self.thread1.join()
        logger.info('Joining thread2')
        self.thread2.join()

        self.dest.close()
 
        logger.info('Stopping: %s', self.container)
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()

    def stop_container():
        # send request along to both OneWayPipes...
        shutdown()
