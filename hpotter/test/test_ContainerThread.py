import unittest

from hpotter.plugins.ContainerThread import ContainerThread

class TestContainerThread(unittest.TestCase):

    def test_TestDynamicFireWallRule1(self):
        source_ip = "192.168.1.1"
        netmask = "255.255.255.255"     # When the subnet mask is not specified by the user, it defaults to this
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"

        result = ContainerThread.create_rules(self, source_ip, source_port, destination_ip, destination_port)[0]
        expected_src = source_ip + "/" + netmask

        self.assertEqual(result[0].src, expected_src)
        self.assertEqual(result[0].matches[0].sport, source_port)
