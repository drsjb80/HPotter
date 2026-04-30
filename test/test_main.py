import unittest
import tempfile
import os
import yaml
from unittest.mock import Mock

from src.__main__ import GracefulKiller, fix_string, HP


class TestMain(unittest.TestCase):
    def test_gracefulkiller_sets_flag(self):
        g = GracefulKiller()
        self.assertFalse(g.kill_now)
        g.exit_gracefully(None, None)
        self.assertTrue(g.kill_now)

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
            hp._read_container_yaml(fname)
            # first serial should have been incremented
            with open(fname) as tf2:
                reloaded = list(yaml.safe_load_all(tf2))
            self.assertEqual(reloaded[0]['serial'], 6)
            # two listen threads should exist and be started
            self.assertEqual(len(hp.listen_threads), 2)
        finally:
            os.remove(fname)
