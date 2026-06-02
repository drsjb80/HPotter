'''Prometheus metrics integration for HPotter.

This module defines the metrics objects used by the application. If the
`prometheus_client` package is unavailable, the symbols become no-op objects
so the rest of the application can still import and use them safely.
'''

try:
    from prometheus_client import Counter, Gauge, start_http_server
    METRICS_ENABLED = True
except ImportError:  # pragma: no cover
    METRICS_ENABLED = False

    def start_http_server(*args, **kwargs):
        return None

    class _DummyMetric:
        def inc(self, amount=1):
            return None

        def dec(self, amount=1):
            return None

        def set(self, value):
            return None

    Counter = _DummyMetric
    Gauge = _DummyMetric

connections_started_total = Counter(
    'hpotter_connections_started_total',
    'Total number of accepted connections handled by HPotter'
)
active_connections = Gauge(
    'hpotter_active_connections',
    'Current number of active HPotter connection handlers'
)
listen_threads_total = Gauge(
    'hpotter_listen_threads_total',
    'Number of active HPotter listen threads'
)
