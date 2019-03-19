import platform
import docker

from hpotter.tables import HTTPCommands
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread

class Singletons():
    httpd_container = None
    httpd_thread = None

def rm_container():
    if Singletons.httpd_container:
        logger.info('Stopping httpd_container')
        Singletons.httpd_container.stop()
        logger.info('Removing httpd_container')
        Singletons.httpd_container.remove()
        Singletons.httpd_container = None
    else:
        logger.info('No httpd_container to stop')

def start_server():     # leave these two in place
    try:
        client = docker.from_env()

        # create apache2 or random dir?
        machine = ''
        tag = 'latest'
        if platform.machine() == 'armv6l':
            machine = 'arm32v6/'
            tag = 'alpine'

        Singletons.httpd_container = client.containers.run(\
            machine + 'httpd:' + tag, \
            detach=True, ports={'80/tcp': 8080}, read_only=True, \
            volumes={'apache2': \
                {'bind': '/usr/local/apache2/logs', 'mode': 'rw'}})
        logger.info('Created: %s', Singletons.httpd_container)

    except OSError as err:
        logger.info(err)
        if Singletons.httpd_container:
            logger.info(Singletons.httpd_container.logs())
            rm_container()
        return

    Singletons.httpd_thread = PipeThread(('0.0.0.0', 80), \
        ('127.0.0.1', 8080), HTTPCommands, 4096)
    Singletons.httpd_thread.start()

def stop_server():
    Singletons.httpd_thread.request_shutdown()
    rm_container()
