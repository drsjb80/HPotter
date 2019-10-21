import os
import platform
import docker
import sys
import subprocess

from hpotter.plugins.plugin import Plugin
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread
from hpotter.plugins import ssh, telnet

class Singletons():
    active_plugins = {}

def start_plugins():
    #ensure Docker is running
    try:
        s = subprocess.check_output('docker ps', shell=True)
    except subprocess.CalledProcessError:
        print("Ensure Docker is running, and please try again.")
        sys.exit()

    ssh.start_server()
    telnet.start_server()

    all_plugins = Plugin.read_in_all_plugins()
    current_thread = None
    current_container = None
    for plugin in all_plugins:
        if plugin is not None:
            try:
                client = docker.from_env()

                container = plugin.container
                if platform.machine() == 'armv6l' :
                    container = plugin.alt_container

                try:
                    for cmd in plugin.setup['mkdir']:
                        logger.info("%s created the %s directory", plugin.name, cmd)
                        os.mkdir(cmd)
                except FileExistsError:
                    pass
                except OSError as error:
                    logger.info(error)
                    return

                if (plugin.volumes):
                    current_container = client.containers.run(container, \
                        detach=plugin.detach, ports=plugin.makeports(), \
                        environment=[plugin.environment])

                else:
                    current_container = client.containers.run(container, \
                        detach=plugin.detach, ports=plugin.makeports(), \
                        read_only=True)

                logger.info('Created: %s', plugin.name)

            except OSError as err:

                logger.info(err)
                if current_container:
                    logger.info(current_container.logs())
                    rm_container()
                return

            current_thread = PipeThread((plugin.listen_address, \
                plugin.listen_port), (plugin.ports['connect_address'], \
                plugin.ports['connect_port']), plugin.table, plugin.capture_length, request_type=plugin.request_type)

            current_thread.start()
            p_dict = {
                "plugin" : plugin,
                "container" : current_container,
                "thread" : current_thread
            }
            Singletons.active_plugins[plugin.name] = p_dict
        else:
            logger.info("yaml configuration seems to be missing some important information")

def stop_plugins():
    ssh.stop_server()
    telnet.stop_server()

    for name, item in Singletons.active_plugins.items():
        try:
            for cmd in item["plugin"].teardown['rmdir']:
                logger.info("---%s is removing the %s directory", name, cmd)
                os.rmdir(cmd)
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass
        except OSError as error:
            logger.info(name + ": " + str(error))
            return

        if item["container"] is not None:
            item["thread"].request_shutdown()
        logger.info("--- removing %s container", item["plugin"].name)
        item["container"].stop()
        logger.info("--- %s container removed", item["plugin"].name)
