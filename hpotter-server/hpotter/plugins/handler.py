import os
import platform
import docker
import re
import sys
import subprocess
import yaml

from hpotter.tables import SQL, SQL_COMMAND_LENGTH
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread
from hpotter.plugins import ssh, telnet

class Singletons():
    active_plugins = {}

class Plugin(yaml.YAMLObject):
    yaml_tag = u'!plugin'
    def __init__(self, name=None, setup=None, teardown=None, container=None, alt_container=None, read_only=None, detach=None, ports=None, tls=None, volumes=None, environment=None, listen_address=None, listen_port=None, table=None, capture_length=None, request_type=None):
        self.name = name
        self.setup = setup
        self.teardown = teardown
        self.container = container
        self.alt_container = alt_container
        self.read_only = read_only
        self.detach = detach
        self.ports = ports
        self.tls = tls
        self.volumes = volumes
        self.environment = environment
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.table = table
        self.capture_length = capture_length
        self.request_type = request_type

    def __repr__(self):
        return "%s( name: %r \n setup: %r \n teardown: %r \n container: %r\n read_only: %r\n detach: %r\n ports: %r \n tls: %r \n volumes: %r \n environment: %r \n listen_address: %r \n listen_port: %r \n table: %r \n capture_length: %r \n request_type: %r)" % (
        self.__class__.__name__, self.name, self.setup,
        self.teardown, self.container, self.read_only, self.detach,
        self.ports, self.tls, self.volumes, self.environment, self.listen_address,
        self.listen_port, self.table, self.capture_length, self.request_type)

    def contains_volumes(self):
        return self.volumes == []

    def makeports(self):
        return {self.ports["from"] : self.ports["connect_port"]}

    @staticmethod
    def read_in_plugins(container_name):
        present = False
        with open('hpotter/plugins/plugins.yml') as file:
            for data in yaml.load_all(Loader=yaml.FullLoader, stream=file):
                if (data["name"] == container_name):
                    present = True
                    return Plugin(name=data['name'], \
                              setup=data['setup'], \
                              teardown=data['teardown'], \
                              container=data['container'], \
                              alt_container=data['alt_container'], \
                              read_only=data['read_only'], \
                              detach=data['detach'], \
                              ports=data['ports'], \
                              tls=data['tls'],\
                              volumes=data['volumes'], \
                              environment=data['environment'], \
                              listen_address=data['listen_address'], \
                              listen_port=data['listen_port'], \
                              table=data['table'], \
                              capture_length=data['capture_length'], request_type=data['request_type'])
            if (present == None):
                print("plugin definintion not present")

    @staticmethod
    def read_in_all_plugins():
        plugins = []
        with open('hpotter/plugins/plugins.yml') as file:
            for data in yaml.load_all(Loader=yaml.FullLoader, stream=file):
                p = Plugin(name=data['name'], setup=data['setup'], \
                          teardown=data['teardown'], container=data['container'], \
                          alt_container=data['alt_container'], \
                          read_only=data['read_only'], detach=data['detach'], \
                          ports=data['ports'], tls=data['tls'],\
                          volumes=data['volumes'], \
                          environment=data['environment'], \
                          listen_address=data['listen_address'], \
                          listen_port=data['listen_port'], table=data['table'], \
                          capture_length=data['capture_length'], request_type=data['request_type'])

                plugins.append(p)
        return plugins

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
                plugin.ports['connect_port']), plugin.table, \
                plugin.capture_length, request_type=plugin.request_type)

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
