import unittest

from hpotter.plugins.ContainerThread import ContainerThread

class TestContainerThread(unittest.TestCase):

    def test_TestDynamicFireWallRule1Src(self):
        source_ip = "192.168.1.1"
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"

        result = ContainerThread.create_rules(self, source_ip, source_port, destination_ip, destination_port)

        self.assertEqual(result[0].src, source_ip)
        self.assertEqual(result[0].matches[0].sport, source_port)
