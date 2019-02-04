import unittest
import socket
from unittest.mock import Mock, MagicMock, call
from hpotter.plugins.telnet import TelnetHandler
from hpotter.plugins.telnet import start_server, stop_server
from hpotter.env import start_shell, stop_shell

class TestTelnet(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_Creds(self):
        tosend = "root\ntoor\nexit\n"
        request = unittest.mock.Mock()
        request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]

        server = unittest.mock.MagicMock()
        th = TelnetHandler(request, ['127.0.0.1', 23], server)
        stop_shell()

        # print(request.mock_calls)

        request.sendall.assert_has_calls([ \
            call(b'Username: '),
            call(b'Password: '),
            call(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\n'),
            call(b'\n$: ')]
        )

    def test_NoCreds(self):
        tosend = "\n\n\n\n\n\n"
        request = unittest.mock.Mock()
        request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]

        server = unittest.mock.MagicMock()

        th = TelnetHandler(request, ['127.0.0.1', 23], server)

        request.sendall.assert_has_calls([ \
            call(b'Username: '),
            call(b'Username: '),
            call(b'Username: ')])
