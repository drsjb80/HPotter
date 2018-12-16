import socket
import unittest
from unittest.mock import Mock
from hpotter.inactive_plugins.generic import GenericHandler, get_addresses

class TestGeneric(unittest.TestCase):
    def test_get_address(self):
        self.assertEqual(get_addresses(),
            [(socket.AF_INET, '127.0.0.1', 2000),(socket.AF_INET6, '::1', 2000)])

    def test_GenericTCPHandler(self):
        # mock the server, socket, and sqlalchemy engine.
        test_server = unittest.mock.Mock()
        test_server.mysocket = unittest.mock.Mock()
        test_server.mysocket.getsockname.return_value = ['127.0.0.1', '2001']
        test_server.engine = unittest.mock.Mock()

        test_request = unittest.mock.Mock()
        test_request.recv.return_value = "foobar"
        GenericHandler.undertest = True
        GenericHandler.session = unittest.mock.Mock()
        GenericHandler(test_request, ['127.0.0.1', 2000], test_server)
        test_request.sendall.assert_called_with("FOOBAR")
