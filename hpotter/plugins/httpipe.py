import docker
import hpotter

from hpotter.tables import HTTPCommands
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread

def rm_container():
    if hpotter.env.httpd_container:
        logger.info('Stopping httpd_container')
        hpotter.env.httpd_container.stop()
        logger.info('Removing httpd_container')
        hpotter.env.httpd_container.remove()
        hpotter.env.httpd_container = None
    else:
        logger.info('No httpd_container to stop')

def start_server():     # leave these two in place
    # machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''
    try:
        client = docker.from_env()

        # create apache2 or random dir?
        hpotter.env.httpd_container = client.containers.run('httpd:latest', \
            detach=True, ports={'80/tcp': 8080}, read_only=True, \
            volumes={'apache2': {'bind': '/usr/local/apache2', 'mode': 'rw'}})
        logger.info('Created: %s', hpotter.env.httpd_container)

    except OSError as err:
        logger.info(err)
        if hpotter.env.httpd_container:
            logger.info(hpotter.env.httpd_container.logs())
            rm_container()
        return

    hpotter.env.httpd_thread = PipeThread(('0.0.0.0', 80), \
        ('127.0.0.1', 8080), HTTPCommands, 4096)
    hpotter.env.httpd_thread.start()

def stop_server():
    hpotter.env.httpd_thread.request_shutdown()
    rm_container()
