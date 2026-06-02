import unittest
import tempfile
import os
import threading
import yaml
from unittest.mock import Mock, patch

from src.app import GracefulKiller, fix_string, HP


class TestMain(unittest.TestCase):
    def test_gracefulkiller_sets_event(self):
        shutdown_event = threading.Event()
        g = GracefulKiller(shutdown_event)
        self.assertFalse(shutdown_event.is_set())
        g.exit_gracefully(None, None)
        self.assertTrue(shutdown_event.is_set())

    def test_fix_string_quotes(self):
        dumper = Mock()
        dumper.represent_scalar.return_value = 'result'
        out = fix_string(dumper, 'hello')
        dumper.represent_scalar.assert_called_with('tag:yaml.org,2002:str', 'hello', style="'")
        self.assertEqual(out, 'result')

    def test_read_container_yaml_increments_serial_and_starts(self):
        hp = HP()
        hp.database = Mock()

        containers = [
            {'container': 'c1', 'serial': 5},
            {'container': 'c2'}
        ]
        # write to temp file
        with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
            yaml.dump_all(containers, tf)
            fname = tf.name

        try:
            # Mock ListenThread so the test exercises only the serial-increment
            # logic and doesn't bind real sockets / start real threads.
            with patch('src.app.ListenThread') as mock_listen_thread:
                hp._read_container_yaml(fname)
            # first serial should have been incremented
            with open(fname) as tf2:
                reloaded = list(yaml.safe_load_all(tf2))
            self.assertEqual(reloaded[0]['serial'], 6)
            # two listen threads should have been created and started
            self.assertEqual(len(hp.listen_threads), 2)
            self.assertEqual(mock_listen_thread.call_count, 2)
            self.assertEqual(mock_listen_thread.return_value.start.call_count, 2)
        finally:
            os.remove(fname)
