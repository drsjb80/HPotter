import unittest

from hpotter.plugins.ContainerThread import ContainerThread

class TestContainerThread(unittest.TestCase):

    def test_TestDynamicFireWallSrc1(self):
        source_ip = "142.56.0.1"
        source_port = "8080"
        destination_ip = "172.168.1.1"
        destination_port = "8081"

        result = ContainerThread.start_dynamic_firewall(self, source_ip, source_port, destination_ip, destination_port)

        self.assertEqual(result[0].src, source_ip)

    def test_TestDynamicFirewallDst1(self):
        source_ip = "142.56.0.1"
        source_port = "8080"
        destination_ip = "172.168.1.1"
        destination_port = "8081"

        result = ContainerThread.start_dynamic_firewall(self, source_ip, source_port, destination_ip, destination_port)

        self.assertEqual(result[0].dst, destination_ip)

    def test_DynamicFirewallSport1(self):
        source_ip = "142.56.0.1"
        source_port = "8080"
        destination_ip = "172.168.1.1"
        destination_port = "8081"

        result = ContainerThread.start_dynamic_firewall(self, source_ip, source_port, destination_ip, destination_port)

        self.assertEqual(result[0].matches[0].sport, source_port)

    def test_DynamicFirewallDport1(self):
        source_ip = "142.56.0.1"
        source_port = "8080"
        destination_ip = "172.168.1.1"
        destination_port = "8081"

        result = ContainerThread.start_dynamic_firewall(self, source_ip, source_port, destination_ip, destination_port)

        self.assertEqual(result[0].matches[0].dport, destination_port)