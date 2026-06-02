import unittest
from unittest.mock import Mock

from src.metrics import (
    METRICS_ENABLED,
    active_connections,
    connections_started_total,
    listen_threads_total,
)
from src.listen_thread import ListenThread


class TestMetrics(unittest.TestCase):
    def setUp(self):
        if not METRICS_ENABLED:
            self.skipTest('prometheus_client not installed')
        active_connections.set(0)
        listen_threads_total.set(0)

    def test_gauges_may_be_set(self):
        active_connections.set(2)
        self.assertEqual(active_connections._value.get(), 2)

        listen_threads_total.set(7)
        self.assertEqual(listen_threads_total._value.get(), 7)

    def test_counter_increments(self):
        base_value = connections_started_total._value.get()
        connections_started_total.inc()
        self.assertEqual(connections_started_total._value.get(), base_value + 1)

    def test_run_container_thread_decrements_active_connections(self):
        active_connections.set(1)

        lt = ListenThread({'listen_port': 9999, 'container': 'x'}, Mock())

        class DummyThread:
            def run(self):
                raise RuntimeError('handler error')

        with self.assertRaises(RuntimeError):
            lt._run_container_thread(DummyThread())

        self.assertEqual(active_connections._value.get(), 0)
