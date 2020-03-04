import socket
import threading
import docker
import time
import iptc
from enum import Enum

from hpotter.logger import logger
from hpotter.plugins.OneWayThread import OneWayThread

class ContainerThread(threading.Thread):
    def __init__(self, source, connection, config):
        super().__init__()
        self.source = source
        self.connection = connection
        self.config = config
        self.container_ip = self.container_port = self.container_protocol = None
        self.dest = self.thread1 = self.thread2 = self.container = None

    '''
    Need to make a different one for macos as docker desktop for macos
    doesn't allow connecting to a docker-defined network. I'm thinking of
    using 127.0.0.1 and mapping the internal port to one in the range
    25000-25999 as those don't appear to be claimed in
    https://support.apple.com/en-us/HT202944
    I believe client sockets start in the 40000's
    '''
    def connect_to_container(self):
        nwsettings = self.container.attrs['NetworkSettings']
        self.container_ip = nwsettings['Networks']['bridge']['IPAddress']
        logger.debug(self.container_ip)

        ports = nwsettings['Ports']
        assert len(ports) == 1

        for p in ports.keys():
            self.container_port = int(p.split('/')[0])
            self.container_protocol = p.split('/')[1]
        logger.debug(self.container_port)
        logger.debug(self.container_protocol)

        for x in range(9):
            try:
                self.dest = socket.create_connection( \
                    (self.container_ip, self.container_port), timeout=2)
                self.dest.settimeout(None)
                logger.debug(self.dest)
                return
            except Exception as err:
                logger.debug(err)
                time.sleep(2)

        logger.info('Unable to connect to ' + self.container_ip + ':' + \
            self.container_port)
        logger.info(err)
        raise err

    def create_rules(self, src_ip, src_port, dest_ip, dest_port, protocol):
        """
        TODO: Create chain named after container hash by getting the 'id' value from the container
        TODO: Create rule that will have the forward chain read the rule in the chain named after the container hash
        Creates rules for the dynamic firewall
            1) Allow the attacker to send packets to the container
            2) Allow the attacker to receive packets from the container
            3) Drop any packets leaving the container and going somewhere that is not the attacker

        Can improve by creating a rule in the forwarding chain that will 'goto' the chain named using the container
        hash for the forwarding rules

        The returned array is used to shutdown the dynamic firewall by removing all of the created rules
        If the program crashes before the end_dynamic_firewall() call, the table will need to be cleared manually

        :param src_ip: Attacker's IP string
        :param src_port: Attacker's port string
        :param dest_ip: Container's IP string
        :param dest_port: Container's Port string
        :param protocol: protocol of the connection (must be string)
        :return rule[]: Rule array returned for usage in start_dynamic_firewall() and end_dynamic_firewall()
        """
        src_rule = {'src': src_ip,
                    'dst': dest_ip,
                    'protocol': protocol,
                    'target': 'ACCEPT',
                    protocol: {'sport': str(src_port),
                            'dport': str(dest_port)}}

        dest_rule = {'src': dest_ip,
                    'dst': src_ip,
                    'protocol': protocol,
                    'target': 'ACCEPT',
                    protocol: {'sport': str(dest_port),
                            'dport': str(src_port)}}

        drop_rule = {'src': dest_ip,
                    'dst': "!" + src_ip,
                    'protocol': protocol,
                    'target': 'DROP',
                    protocol: {'sport': str(dest_port}}

        return [src_rule, dest_rule, drop_rule]

    def start_dynamic_firewall(self, rule_arr):
        for rule in rule_arr:
            iptc.easy.add_rule('filter', 'FORWARD', rule)

    def end_dynamic_firewall(self, rule_arr):
        for rule in rule_arr:
            iptc.easy.delete_rule('filter', 'FORWARD', rule)

    def run(self):
        try:
            client = docker.from_env()
            self.container = client.containers.run(self.config['container'], detach=True)
            logger.info('Started: %s', self.container)
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

        rules = self.create_rules(self.source.getSockName()[0], self.source.getSockName()[1],
                                  self.container_ip, self.container_port, self.container_protocol)

        # startup dynamic iptables rules code here.
        self.start_dynamic_firewall(rules)

        logger.debug('Starting thread1')
        self.thread1 = OneWayThread(self.source, self.dest, self.connection, self.config, 'request')
        self.thread1.start()

        logger.debug('Starting thread2')
        self.thread2 = OneWayThread(self.dest, self.source, self.connection, self.config, 'response')
        self.thread2.start()

        logger.debug('Joining thread1')
        self.thread1.join()
        logger.debug('Joining thread2')
        self.thread2.join()

        # shutdown dynamic iptables rules code here.
        self.end_dynamic_firewall(rules)

        self.dest.close()
        self.stop_and_remove()

    def stop_and_remove(self):
        logger.debug(str(self.container.logs()))
        logger.info('Stopping: %s', self.container)
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()

    def shutdown(self):
        self.thread1.shutdown()
        self.thread2.shutdown()
        self.dest.close()
        self.stop_and_remove()

