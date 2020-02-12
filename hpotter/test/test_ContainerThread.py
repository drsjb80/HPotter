import unittest
import iptc

from hpotter.plugins.ContainerThread import ContainerThread

class TestContainerThread(unittest.TestCase):
    #   TODO: Encapsulate the changes made to the filter table so that the tests do not actually make changes to it

    def test_TestDynamicFireWallRule1(self):
        source_ip = "192.168.1.1"
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"
        mock = unittest.mock.Mock()
        mock = ContainerThread()

        result = ContainerThread.start_dynamic_firewall(mock, source_ip, source_port, destination_ip, destination_port)

        filter = iptc.Table(iptc.Table.FILTER)
        filter.flush()

        self.assertEqual(result[0].src, source_ip)
