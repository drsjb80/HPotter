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
