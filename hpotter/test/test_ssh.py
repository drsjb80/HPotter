import unittest
import socket
from unittest.mock import Mock, call
from hpotter.plugins.ssh import get_addresses
from hpotter.plugins.ssh import SSHServer

class TestSsh(unittest.TestCase):
	def setUp(self):
		SSHServer.undertest=True
 
	def test_get_addresses(self):
		self.assertEqual(get_addresses(),[(socket.AF_INET, '0.0.0.0', 22)])
