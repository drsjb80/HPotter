import unittest

from hpotter.plugins.ContainerThread import ContainerThread

class TestContainerThread(unittest.TestCase):

    def test_TestDynamicFirewallRule1(self):
        source_ip = "192.168.1.1"
        netmask = "255.255.255.255"     # When the subnet mask is not specified by the user, it defaults to this
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"

        result = ContainerThread.create_rules(self, source_ip, source_port, destination_ip, destination_port)[0]
        real_src = source_ip + "/" + netmask
        real_dst = destination_ip + "/" + netmask

        self.assertEqual(result.src, real_src)
        self.assertEqual(result.matches[0].sport, source_port)
        self.assertEqual(result.dst, real_dst)
        self.assertEqual(result.matches[0].dport, destination_port)
        self.assertEqual(result.protocol, "tcp")

    def test_TestDynamicFirewallRule2(self):
        source_ip = "192.168.1.1"
        netmask = "255.255.255.255"  # When the subnet mask is not specified by the user, it defaults to this
        source_port = "8080"
        destination_ip = "172.161.1.1"
        destination_port = "8081"

        result = ContainerThread.create_rules(self, source_ip, source_port, destination_ip, destination_port)[1]
        real_src = source_ip + "/" + netmask
        real_dst = destination_ip + "/" + netmask

        self.assertEqual(result.src, real_dst)
        self.assertEqual(result.matches[0].sport, destination_port)
        self.assertEqual(result.dst, real_src)
        self.assertEqual(result.matches[0].dport, source_port)
        self.assertEqual(result.protocol, "tcp")

    # TODO: Since this rule inverts the destination there needs to be a way to make sure that the rule is inverted
    # The actual destination address is not changed. Relevant lines in iptc.py [1111 - 1153]
    '''
    def test_TestDynamicFirewallRule3(self):
        print("TODO")
    '''



