import unittest

from hpotter.plugins.ContainerThread import ContainerThread

class TestContainerThread(unittest.TestCase):

    def test_TestDynamicFirewallRule1(self):
        source_ip = "192.168.1.1"
        netmask = "255.255.255.255"     # When the subnet mask is not specified by the user, it defaults to this
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"
        protocol = "tcp"

        source = source_ip + "/" + netmask
        destination = destination_ip + "/" + netmask

        result = ContainerThread.create_rules(source_ip, source_port, destination_ip, destination_port, protocol)[0]

        self.assertEqual(result['src'], source)
        self.assertEqual(result['dst'], destination)
        self.assertEqual(result[protocol]['sport'], source_port)
        self.assertEqual(result[protocol]['dport'], destination_port)
        self.assertEqual(result['protocol'], protocol)


    def test_TestDynamicFirewallRule2(self):
        source_ip = "192.168.1.1"
        netmask = "255.255.255.255"  # When the subnet mask is not specified by the user, it defaults to this
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"
        protocol = "tcp"

        source = source_ip + "/" + netmask
        destination = destination_ip + "/" + netmask

        result = ContainerThread.create_rules(source_ip, source_port, destination_ip, destination_port, protocol)[1]

        self.assertEqual(result['src'], destination)
        self.assertEqual(result['dst'], source)
        self.assertEqual(result[protocol]['sport'], destination_port)
        self.assertEqual(result[protocol]['dport'], source_port)
        self.assertEqual(result['protocol'], protocol)

    # TODO: Since this rule inverts the destination there needs to be a way to make sure that the rule is inverted
    # The actual destination address is not changed. Relevant lines in iptc.py [1111 - 1153]
    '''
    def test_TestDynamicFirewallRule3(self):
        print("TODO")
    '''



