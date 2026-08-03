"""VPN/datacenter IP detection for HPotter.

Identifies connections from known VPN and hosting providers by checking
the source IP's ASN (Autonomous System Number) against a list of known
datacenter/VPN provider ASNs.

Uses ip-api.com for ASN lookups with in-memory caching to minimize API calls.
"""

import threading

import requests

from src.logger import logger

DATACENTER_ASNS = {
    # AWS
    16509, 14061, 13174, 54115, 63949, 35994, 61871,
    # Microsoft Azure
    8075, 8068,
    # Google Cloud
    15169, 19527,
    # Vultr
    20473,
    # Hetzner
    24940,
    # OVH
    16276,
    # Contabo
    51167,
    # FastHTTP
    39798,
    # Hurricane Electric
    6939,
    # NForce Entertainment
    8452,
    # ColoCrossing
    36352,
    # Packet (Equinix Metal)
    33387,
    # Scaleway
    12876,
    # Upcloud
    9822,
    # Exoscale
    197068,
}


class VPNChecker:
    """Manages VPN/datacenter IP detection via ASN lookup."""

    IPAPI_URL = 'https://ip-api.com/json/{ip}'
    CACHE_MAX_SIZE = 10000

    def __init__(self):
        self.asn_cache = {}
        self.lock = threading.Lock()

    def _get_asn(self, ip_str):
        """Fetch ASN for an IP address using ip-api.com.

        Returns ASN as integer, or None if lookup fails.
        """
        try:
            response = requests.get(
                self.IPAPI_URL.format(ip=ip_str),
                timeout=5,
                params={'fields': 'as'}
            )
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'success' and 'as' in data:
                asn_str = data['as']
                if asn_str.startswith('AS'):
                    return int(asn_str[2:])
            return None
        except Exception as exc:
            logger.debug(f'Failed to look up ASN for {ip_str}: {exc}')
            return None

    def is_vpn(self, ip_str):
        """Check if an IP is from a known VPN/datacenter provider.

        Args:
            ip_str: IP address string

        Returns:
            True if the IP's ASN matches a known VPN/datacenter provider.
        """
        with self.lock:
            if ip_str in self.asn_cache:
                asn = self.asn_cache[ip_str]
            else:
                asn = self._get_asn(ip_str)
                if len(self.asn_cache) < self.CACHE_MAX_SIZE:
                    self.asn_cache[ip_str] = asn

        if asn is None:
            logger.debug(f'ASN lookup failed for {ip_str}, treating as non-VPN')
            return False

        is_datacenter = asn in DATACENTER_ASNS
        logger.debug(f'IP {ip_str}: ASN {asn}, datacenter={is_datacenter}')
        return is_datacenter


_checker = None


def init_vpn_checker():
    """Initialize the global VPN checker instance."""
    global _checker
    try:
        _checker = VPNChecker()
        logger.info('VPN checker initialized')
        return True
    except Exception as exc:
        logger.warning(f'VPN checker initialization failed: {exc}')
        return False


def is_vpn(ip_str):
    """Check if an IP is likely a VPN/datacenter IP.

    Returns False gracefully if the VPN checker failed to initialize.
    """
    if _checker is None:
        return False
    return _checker.is_vpn(ip_str)
