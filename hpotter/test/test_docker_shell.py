import unittest
from unittest.mock import MagicMock, call
from hpotter.docker.shell import cd

class TestTelnet(unittest.TestCase):
    def test_empty_cd(self):
        self.assertEqual(cd('cd', '/'), '/')
        self.assertEqual(cd('cd', '/foo/bar'), '/foo/bar')

    def test_dotdot_cd(self):
        self.assertEqual(cd('cd ..', '/foo/bar'), '/foo')
        self.assertEqual(cd('cd ../..', '/foo/bar'), '/')
        self.assertEqual(cd('cd ../../', '/foo/bar'), '/')
        self.assertEqual(cd('cd ..', '/foo'), '/')
        self.assertEqual(cd('cd ..', '/'), '/')
        self.assertEqual(cd('cd ../', '/foo/bar'), '/foo')
        self.assertEqual(cd('cd ../baz', '/foo/bar'), '/foo/baz')

    def test_dot_cd(self):
        self.assertEqual(cd('cd .', '/'), '/')
        self.assertEqual(cd('cd .', '/foo/bar'), '/foo/bar')

    def test_mixed_dot_cd(self):
        self.assertEqual(cd('cd ./.', '/foo/bar'), '/foo/bar')
        self.assertEqual(cd('cd ././.', '/foo/bar'), '/foo/bar')
        self.assertEqual(cd('cd ./../.', '/foo/bar'), '/foo')
        self.assertEqual(cd('cd .././.', '/foo/bar'), '/foo')
        self.assertEqual(cd('cd ../../.', '/foo/bar'), '/')
        self.assertEqual(cd('cd ../../..', '/foo/bar'), '/')

    def test_absolute_cd(self):
        self.assertEqual(cd('cd /', '/foo/bar'), '/')
        self.assertEqual(cd('cd /', '/'), '/')

    def test_relative_cd(self):
        self.assertEqual(cd('cd etc', '/'), '/etc')
        self.assertEqual(cd('cd etc', '/etc'), '/etc/etc')
        
