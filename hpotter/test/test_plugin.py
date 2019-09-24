import unittest
from unittest.mock import MagicMock, call
from hpotter.plugins.plugin import Plugin

class TestPlugin(unittest.TestCase):
    def test_init(self):
        self.name = unittest.mock.Mock()
        self.setup = unittest.mock.Mock()
        self.teardown = unittest.mock.Mock()
        self.container = unittest.mock.Mock()
        self.alt_container = unittest.mock.Mock()
        self.read_only = unittest.mock.Mock()
        self.detach = unittest.mock.Mock()
        self.ports = unittest.mock.Mock()
        self.volumes = unittest.mock.Mock()
        self.environment = unittest.mock.Mock()
        self.listen_address = unittest.mock.Mock()
        self.listen_port = unittest.mock.Mock()
        self.table = unittest.mock.Mock()
        self.capture_length = unittest.mock.Mock()

    def test_repr(self):
        return "%s( name: %r \n setup: %r \n teardown: %r \n container: %r\n read_only: %r\n detach: %r\n ports: %r \n volumes: %r \n environment: %r \n listen_address: %r \n listen_port: %r \n table: %r \n capture_length: %r)" % (
        unittest.mock.Mock(), unittest.mock.Mock(), unittest.mock.Mock(),
        unittest.mock.Mock(), unittest.mock.Mock(), unittest.mock.Mock(),
        unittest.mock.Mock(), unittest.mock.Mock(), unittest.mock.Mock(),
        unittest.mock.Mock(), unittest.mock.Mock(), unittest.mock.Mock(),
        unittest.mock.Mock(), unittest.mock.Mock())
