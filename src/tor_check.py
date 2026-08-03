"""Tor exit node detection for HPotter.

Fetches and caches the official Tor exit node list from the Tor Project,
then checks incoming connection IPs against this list.

The list is fetched from: https://check.torproject.org/exit-addresses
"""

import ipaddress
import threading
from datetime import datetime, timedelta, timezone

import requests

from src.logger import logger


class TorChecker:
    """Manages Tor exit node list fetching and caching."""

    TORPROJECT_URL = 'https://check.torproject.org/exit-addresses'
    CACHE_TTL_SECONDS = 3600  # Refresh every hour

    def __init__(self):
        self.exit_ips = set()
        self.last_fetch = None
        self.lock = threading.Lock()
        self._fetch_list()

    def _fetch_list(self):
        """Fetch the Tor exit node list from the Tor Project.

        Parses the exit-addresses format (one IP per line, lines starting
        with "ExitAddress" contain the IPv4 addresses).
        """
        try:
            logger.debug('Fetching Tor exit node list')
            response = requests.get(self.TORPROJECT_URL, timeout=10)
            response.raise_for_status()

            exit_ips = set()
            for line in response.text.splitlines():
                if line.startswith('ExitAddress '):
                    ip_str = line.split()[1]
                    try:
                        ipaddress.ip_address(ip_str)
                        exit_ips.add(ip_str)
                    except ValueError:
                        logger.debug(f'Invalid IP in Tor list: {ip_str}')

            with self.lock:
                self.exit_ips = exit_ips
                self.last_fetch = datetime.now(timezone.utc)
            logger.info(f'Loaded {len(exit_ips)} Tor exit nodes')
        except Exception as exc:
            logger.warning(f'Failed to fetch Tor exit list: {exc}')

    def _refresh_if_stale(self):
        """Refresh the exit list if it's older than CACHE_TTL_SECONDS."""
        if self.last_fetch is None:
            return

        age = datetime.now(timezone.utc) - self.last_fetch
        if age > timedelta(seconds=self.CACHE_TTL_SECONDS):
            self._fetch_list()

    def is_tor_exit(self, ip_str):
        """Check if an IP is a known Tor exit node.

        Args:
            ip_str: IP address string (IPv4 or IPv6)

        Returns:
            True if the IP is in the cached Tor exit list, False otherwise.
        """
        self._refresh_if_stale()

        with self.lock:
            return ip_str in self.exit_ips


# Global instance
_checker = None


def init_tor_checker():
    """Initialize the global Tor checker instance."""
    global _checker
    try:
        _checker = TorChecker()
        return True
    except Exception as exc:
        logger.warning(f'Tor checker initialization failed: {exc}')
        return False


def is_tor_exit(ip_str):
    """Check if an IP is a Tor exit node.

    Returns False gracefully if the Tor checker failed to initialize.
    """
    if _checker is None:
        return False
    return _checker.is_tor_exit(ip_str)
