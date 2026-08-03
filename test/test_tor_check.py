"""Tests for Tor exit node detection."""

import unittest
from unittest.mock import MagicMock, patch

from src.tor_check import TorChecker, is_tor_exit


class TestTorChecker(unittest.TestCase):
    """Test Tor exit node detection."""

    def test_parse_exit_addresses(self):
        """Test parsing of Tor exit addresses format."""
        mock_response = MagicMock()
        mock_response.text = """Published 2024-01-15 00:00:00
ExitAddress 192.0.2.1 192.0.2.1
ExitAddress 198.51.100.5 198.51.100.5
ExitAddress 203.0.113.10 203.0.113.10
"""
        with patch('src.tor_check.requests.get', return_value=mock_response):
            checker = TorChecker()
            self.assertIn('192.0.2.1', checker.exit_ips)
            self.assertIn('198.51.100.5', checker.exit_ips)
            self.assertIn('203.0.113.10', checker.exit_ips)

    def test_is_tor_exit(self):
        """Test checking if an IP is a Tor exit."""
        mock_response = MagicMock()
        mock_response.text = """ExitAddress 192.0.2.1 192.0.2.1
ExitAddress 198.51.100.5 198.51.100.5
"""
        with patch('src.tor_check.requests.get', return_value=mock_response):
            checker = TorChecker()
            self.assertTrue(checker.is_tor_exit('192.0.2.1'))
            self.assertTrue(checker.is_tor_exit('198.51.100.5'))
            self.assertFalse(checker.is_tor_exit('203.0.113.10'))

    def test_invalid_ip_skipped(self):
        """Test that invalid IPs in the list are skipped."""
        mock_response = MagicMock()
        mock_response.text = """ExitAddress invalid-ip not-an-ip
ExitAddress 192.0.2.1 192.0.2.1
"""
        with patch('src.tor_check.requests.get', return_value=mock_response):
            checker = TorChecker()
            self.assertIn('192.0.2.1', checker.exit_ips)
            self.assertEqual(len(checker.exit_ips), 1)

    def test_fetch_failure_graceful(self):
        """Test that fetch failures don't crash the application."""
        with patch('src.tor_check.requests.get', side_effect=Exception('Network error')):
            checker = TorChecker()
            self.assertEqual(len(checker.exit_ips), 0)

    def test_is_tor_exit_graceful(self):
        """Test that is_tor_exit returns False if checker is not initialized."""
        result = is_tor_exit('192.0.2.1')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
