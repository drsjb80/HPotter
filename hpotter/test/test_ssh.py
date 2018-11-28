import unittest
from unittest.mock import Mock, call
from plugins.ssh import get_addresses

class TestSsh(unittest.TestCase):
	def setUp(self):
		TelnetHandler.undertest=True
 
	def test_get_addresses(self):
		self.assertEqual(get_addresses(),[(socket.AF_INET, '0.0.0.0', 22)])