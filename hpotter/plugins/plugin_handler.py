import os
import platform
import docker
import re

from hpotter.plugins.plugin import Plugin
from hpotter.tables import SQL, SQL_COMMAND_LENGTH
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread
from hpotter.plugins import ssh, telnet

class Singletons():
    numPlugins = 2
    containers = [None]*numPlugins
    threads = [None]*numPlugins
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

def start_server(plugin_name, index):
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
            rm_container()
        return

    Singletons.current_thread = PipeThread((current.listen_address, \
        current.listen_port), (current.ports['connect_address'], \
        current.ports['connect_port']), current.table, current.capture_length)

    Singletons.current_thread.start()
    Singletons.containers[index] = Singletons.current_container
    Singletons.threads[index] = Singletons.current_thread

def stop_server(plugin_name):
    if Singletons.current_container is not None:
        Singletons.current_thread.request_shutdown()
    rm_container()

def stop_all_running_containers():
    index = 0
    for container in Singletons.containers:
        if container is not None:
            Singletons.current_container = container
            Singletons.current_thread = Singletons.threads[index]

            if Singletons.current_container is not None:
                Singletons.current_thread.request_shutdown()
            rm_container()

            Singletons.containers[index] = None
            Singletons.threads[index] = None
        else:
            logger.info('container located at position %r is None', index)
        index = index + 1

def start_protocols():
    ssh.start_server()
    telnet.start_server()

def stop_protocols():
    ssh.stop_server()
    telnet.stop_server()
