import unittest
from unittest.mock import Mock, patch

from src.container import Container


class TestContainer(unittest.TestCase):
    def setUp(self):
        # minimal arguments, None values are filled by lazy_init decorator
        self.ct = Container('srcsock', 'conn', {'container': 'foo', 'connection_timeout': 5}, Mock())

    def test_connect_to_container_success(self):
        # fake container attributes with network settings
        self.ct.container = Mock()
        self.ct.container.attrs = {
            'NetworkSettings': {
                'Networks': {'bridge': {'IPAddress': '10.0.0.1'}},
                'Ports': {'1234/tcp': [{}]}
            }
        }

        fake_sock = Mock()

        def fake_create(addr, timeout):
            return fake_sock

        with patch('src.container.socket.create_connection', fake_create):
            self.ct._connect_to_container()
            self.assertEqual(self.ct.container_ip, '10.0.0.1')
            self.assertEqual(self.ct.container_port, 1234)
            self.assertEqual(self.ct.container_protocol, 'tcp')
            self.assertIs(self.ct.dest, fake_sock)

    def test_connect_to_container_failure(self):
        self.ct.container = Mock()
        self.ct.container.attrs = {
            'NetworkSettings': {
                'Networks': {'bridge': {'IPAddress': '10.0.0.1'}},
                'Ports': {'1234/tcp': [{}]}
            }
        }
        with patch('src.container.socket.create_connection', side_effect=Exception('oops')):
            with patch('time.sleep'):  # avoid delays
                with self.assertRaises(ConnectionError):
                    self.ct._connect_to_container()

    def test_start_and_join_threads(self):
        # patch OneWayThread to a simple dummy that records calls
        class DummyThread:
            def __init__(self, src, dest, connection, container_config,
                         direction, database, remote_ip=None):
                self.src = src
                self.dest = dest
                self.connection = connection
                self.container_config = container_config
                self.direction = direction
                self.database = database
                self.remote_ip = remote_ip
                self.started = False
                self.joined = False

            def start(self):
                self.started = True

            def join(self):
                self.joined = True

            def shutdown(self):
                pass

        with patch('src.container.OneWayThread', DummyThread):
            self.ct.source = Mock()
            self.ct.dest = Mock()
            self.ct.source.getpeername.return_value = ('1.2.3.4', 9999)
            self.ct.connection = Mock()
            self.ct.container_config = {'connection_timeout': 5}
            self.ct.database = Mock()
            self.ct._start_and_join_threads()

            self.assertTrue(self.ct.thread1.started and self.ct.thread1.joined)
            self.assertTrue(self.ct.thread2.started and self.ct.thread2.joined)
            # remote_ip should have been passed to second thread
            self.assertEqual(self.ct.thread2.remote_ip, '1.2.3.4')

    def test_shutdown_calls_components(self):
        self.ct.thread1 = Mock()
        self.ct.thread2 = Mock()
        self.ct.dest = Mock()
        self.ct.container = Mock()
        self.ct._stop_and_remove = Mock()
        self.ct.shutdown()
        self.ct.thread1.shutdown.assert_called_once()
        self.ct.thread2.shutdown.assert_called_once()
        self.ct.dest.close.assert_called_once()
        self.ct._stop_and_remove.assert_called_once()
