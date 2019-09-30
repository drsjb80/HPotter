import os
import platform
import docker
import re

from hpotter.plugins.plugin import Plugin
from hpotter.tables import SQL, SQL_COMMAND_LENGTH
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread

class Singletons():
    current_container = None
    current_thread = None

def rm_container():
    if Singletons.current_container:
        logger.info('Stopping httpd_container')
        Singletons.current_container.stop()
        logger.info('Removing httpd_container')
        Singletons.current_container.remove()
        Singletons.current_container = None
    else:
        logger.info('No container to stop')

def start_server(plugin_name):
    current = Plugin.read_in_plugins(container_name=plugin_name)
    try:
        client = docker.from_env()

        container = current.container
        if platform.machine() == 'armv6l' :
            container = current.alt_container

        try:
            for cmd in current.setup['mkdir']:
                os.mkdir(cmd)
        except FileExistsError:
            pass
        except OSError as error:
            logger.info(error)
            return

        if (current.volumes):
            Singletons.current_container = client.containers.run(container, \
                detach=current.detach, ports=current.makeports(), \
                environment=[current.environment])
        else:
            Singletons.httpd_container = client.containers.run(container, \
                detach=current.detach, ports=current.makeports(), \
                read_only=True)

        logger.info('Created: %s', Singletons.current_container)
    except OSError as err:

        logger.info(err)
        if Singletons.current_container:
            logger.info(Singletons.current_container.logs())
            rm_container
        return

    Singletons.current_thread = PipeThread((current.listen_address, \
        current.listen_port), (current.ports['connect_address'], \
        current.ports['connect_port']), current.table, current.capture_length)
    Singletons.current_thread.start()

def stop_server(plugin_name):
    if Singletons.current_container is not None:
        Singletons.current_thread.request_shutdown()
    rm_container()
