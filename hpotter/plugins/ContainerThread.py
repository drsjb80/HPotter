import socket
import threading
import docker
import time
import iptc
from enum import Enum

from hpotter.tables import Connections, TCP

from hpotter.logger import logger
from hpotter.plugins.OneWayThread import OneWayThread

class RorR(Enum):
    request = 1
    response = 2
    neither = 3

class ContainerThread(threading.Thread):
    def __init__(self, db, source, config):
        super().__init__()
        self.db = db
        self.source = source
        self.config = config
        self.connection = None
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
        IPAddress = nwsettings['Networks']['bridge']['IPAddress']
        logger.debug(IPAddress)

        ports = nwsettings['Ports']
        assert len(ports) == 1

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

    def save_connection(self):
        if 'add_dest' in self.config:
            self.connection = Connections(
                sourceIP=self.source.getsockname()[0],
                sourcePort=self.source.getsockname()[1],
                destIP=self.dest.getsockname()[0],
                destPort=self.dest.getsockname()[1],
                proto=TCP)
            self.db.write(self.connection)
        else:
            self.connection = Connections(
                sourceIP=self.source.getsockname()[0],
                sourcePort=self.source.getsockname()[1],
                proto=TCP)
            self.db.write(self.connection)

    def create_rules(self, src_ip, src_port, dest_ip, dest_port):
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
        :return rule[]: Rule array returned for usage in start_dynamic_firewall() and end_dynamic_firewall()
        """

        src_rule = iptc.Rule()
        src_rule.src = src_ip
        src_rule.dst = dest_ip
        src_rule.protocol = "tcp"
        src_rule.create_target("ACCEPT")
        src_match = src_rule.create_match("tcp")
        src_match.sport = src_port
        src_match.dport = dest_port

        dest_rule = iptc.Rule()
        dest_rule.src = dest_ip
        dest_rule.dst = src_ip
        dest_rule.protocol = "tcp"
        dest_rule.create_target("ACCEPT")
        dest_match = dest_rule.create_match("tcp")
        dest_match.sport = dest_port
        dest_match.dport = src_port

        drop_rule = iptc.Rule()
        drop_rule.src = dest_ip
        drop_rule.dst = "!" + src_ip
        drop_rule.create_target("DROP")
        drop_match = drop_rule.create_match("tcp")
        drop_match.sport = dest_port

        return [src_rule, dest_rule, drop_rule]

    def start_dynamic_firewall(self, rule_arr):
        forward_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "FORWARD")
        for rule in rule_arr:
            forward_chain.append_rule(rule)

    def end_dynamic_firewall(self, rule_arr):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "FORWARD")
        for rule in rule_arr:
            chain.delete_rule(rule)


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

        self.save_connection()

        # startup dynamic iptables rules code here.

        rules = self.create_rules(self.source.getsockname()[0], self.source.getsockname()[1],
                                  self.dest.getsockname()[0], self.dest.getsockname()[1])

        self.start_dynamic_firewall(rules)

        logger.debug('Starting thread1')
        self.thread1 = OneWayThread(self.db, self.source, self.dest, \
            {'request_length': 4096}, 'request', self.connection)
        self.thread1.start()
        logger.debug('Starting thread2')
        self.thread2 = OneWayThread(self.db, self.dest, self.source, self.config, 'response', self.connection)
        self.thread2.start()

        logger.debug('Joining thread1')
        self.thread1.join()
        logger.debug('Joining thread2')
        self.thread2.join()

        # shutdown dynamic iptables

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

