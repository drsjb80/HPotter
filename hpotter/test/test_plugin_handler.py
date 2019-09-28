import unittest
from unittest.mock import MagicMock, call
from hpotter.plugins.plugin import*
from hpotter.plugins.plugin_handler import*

class TestPluginHandler(unittest.TestCase):
    def test_rm_container(self):
        rm_container()
        assert(Singletons.current_container == None)
        Singletons.current_container = MagicMock()
        Singletons.current_thread = unittest.mock.Mock()
        rm_container()
        assert(Singletons.current_container == None)

    # def test_start_server(self):
    #     start_server(MagicMock())

    def test_stop_server(self):
        Singletons.current_container = MagicMock()
        stop_server(MagicMock())
        assert(Singletons.current_container == None)
