import unittest
from unittest.mock import MagicMock, call
from hpotter.plugins import*
from hpotter.plugins.plugin_handler import*

class TestPluginHandler(unittest.TestCase):
    def test_rm_container(self):
        rm_container()
        assert(logger.info('No container to stop'))
        Singletons.current_container = MagicMock()
        Singletons.current_thread = unittest.mock.Mock()
        rm_container()
        assert(Singletons.current_container == None)
