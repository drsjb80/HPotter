import unittest
import socket
from unittest.mock import Mock, call
from hpotter.plugins.telnet import TelnetHandler
from hpotter.plugins.telnet import get_addresses

class TestTelnet(unittest.TestCase):
    def setUp(self):
        TelnetHandler.undertest = True
        self.test_server = unittest.mock.Mock()
        self.test_server.mysocket = unittest.mock.Mock()

    def test_Address(self):
        self.assertEqual(get_addresses(), [(socket.AF_INET, '0.0.0.0', 23)])

    def test_TelnetHandler(self):
        tosend = "root\ntoor\nls\nfoo\nexit\n"
        test_request = unittest.mock.Mock()
        test_request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]

        TelnetHandler.session = unittest.mock.Mock()
        TelnetHandler(test_request, ['127.0.0.1', 2000], self.test_server)

        # print(test_request.mock_calls)
        test_request.sendall.assert_has_calls([call(b'Username: '),
            call(b'Password: '),
            call(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\r\n'),
            # call(b'$: '),
            call(b'\r\n$: '),
            # call(b'Servers  Databases   Top_Secret  Documents\r\n'),
            call(b'\r\nbash: ls: command not found'),
            # call(b'$: '),
            call(b'\r\n$: '),
            # call(b'bash: foo: command not found\r\n'),
            call(b'\r\nbash: foo: command not found'),
            # call(b'$: ')])
            call(b'\r\n$: ')])
