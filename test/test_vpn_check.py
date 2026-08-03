"""Tests for VPN/datacenter detection."""

import unittest
from unittest.mock import patch, MagicMock

from src.vpn_check import VPNChecker, is_vpn, DATACENTER_ASNS


class TestVPNChecker(unittest.TestCase):
    """Test VPN/datacenter IP detection."""

    def test_asn_lookup_aws(self):
        """Test ASN lookup for an AWS IP."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'as': 'AS16509'
        }
        with patch('src.vpn_check.requests.get', return_value=mock_response):
            checker = VPNChecker()
            self.assertTrue(checker.is_vpn('52.0.0.1'))

    def test_asn_lookup_azure(self):
        """Test ASN lookup for an Azure IP."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'as': 'AS8075'
        }
        with patch('src.vpn_check.requests.get', return_value=mock_response):
            checker = VPNChecker()
            self.assertTrue(checker.is_vpn('13.0.0.1'))

    def test_asn_lookup_regular_isp(self):
        """Test that regular ISP IPs are not flagged as VPN."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'as': 'AS1234'
        }
        with patch('src.vpn_check.requests.get', return_value=mock_response):
            checker = VPNChecker()
            self.assertFalse(checker.is_vpn('203.0.113.1'))

    def test_asn_caching(self):
        """Test that ASN lookups are cached."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'as': 'AS16509'
        }
        with patch('src.vpn_check.requests.get', return_value=mock_response) as mock_get:
            checker = VPNChecker()
            checker.is_vpn('52.0.0.1')
            checker.is_vpn('52.0.0.1')
            checker.is_vpn('52.0.0.1')
            # Should only call API once due to caching
            self.assertEqual(mock_get.call_count, 1)

    def test_asn_lookup_failure(self):
        """Test that ASN lookup failures are handled gracefully."""
        with patch('src.vpn_check.requests.get', side_effect=Exception('Network error')):
            checker = VPNChecker()
            result = checker.is_vpn('52.0.0.1')
            self.assertFalse(result)

    def test_asn_invalid_response(self):
        """Test handling of invalid ASN API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'fail'}
        with patch('src.vpn_check.requests.get', return_value=mock_response):
            checker = VPNChecker()
            self.assertFalse(checker.is_vpn('52.0.0.1'))

    def test_is_vpn_graceful(self):
        """Test that is_vpn returns False if checker is not initialized."""
        result = is_vpn('52.0.0.1')
        self.assertFalse(result)

    def test_datacenter_asns_populated(self):
        """Test that datacenter ASN list is not empty."""
        self.assertGreater(len(DATACENTER_ASNS), 10)
        self.assertIn(16509, DATACENTER_ASNS)  # AWS
        self.assertIn(8075, DATACENTER_ASNS)   # Azure
        self.assertIn(15169, DATACENTER_ASNS)  # Google Cloud

    def test_asn_cache_size_limit(self):
        """Test that ASN cache doesn't grow unbounded."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'as': 'AS16509'
        }
        with patch('src.vpn_check.requests.get', return_value=mock_response):
            checker = VPNChecker()
            for i in range(VPNChecker.CACHE_MAX_SIZE + 100):
                ip = f'52.0.0.{i % 256}'
                checker.is_vpn(ip)
            self.assertLessEqual(len(checker.asn_cache), VPNChecker.CACHE_MAX_SIZE)


if __name__ == '__main__':
    unittest.main()
