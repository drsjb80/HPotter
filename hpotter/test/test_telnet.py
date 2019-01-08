import unittest
import socket
from unittest.mock import Mock, call
from hpotter.plugins.telnet import TelnetHandler
from hpotter.plugins.telnet import get_addresses, start_server, stop_server

''' All this needs to be fixed for the new docker implementation. '''
class TestTelnet(unittest.TestCase):
    def setUp(self):
        # start_server
        pass

    def tearDown(self):
        # stop_server
        pass

    def test_Address(self):
        self.assertEqual(get_addresses(), [(socket.AF_INET, '0.0.0.0', 23)])

    def test_TelnetHandler(self):
        tosend = "root\ntoor\nfoo\nexit\n"
        '''
        test_request = unittest.mock.Mock()
        test_request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]
        test_request.mysocket.getsockname.side_effect = ['127.0.0.2', 2001]


        test_server = unittest.mock.Mock()
        test_server.mysocket = unittest.mock.MagicMock()
        th = TelnetHandler(test_request, ['127.0.0.1', 2000], test_server)

        print(test_request.mock_calls)
        test_request.sendall.assert_has_calls([call(b'Username: '),
            call(b'Password: '),
            call(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\r\n'),
            call(b'\r\n$: '),
            call(b'\r\nbash: foo: command not found'),
            call(b'\r\n$: ')])
        '''
