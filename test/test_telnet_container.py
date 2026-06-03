import unittest
from unittest.mock import Mock

from src import tables
from src.telnet_container import TelnetContainer


class TestTelnetContainer(unittest.TestCase):
    def test_lazy_init_assigns_attributes(self):
        src = Mock()
        conn = Mock()
        cfg = {
            'container': 'debian:bookworm-slim',
            'listen_port': 23,
            'type': 'telnet'
        }
        db = Mock()
        tc = TelnetContainer(src, conn, cfg, db)
        self.assertIs(tc.source, src)
        self.assertIs(tc.connection, conn)
        self.assertIs(tc.container_config, cfg)
        self.assertIs(tc.database, db)
        self.assertIsNone(tc.container)
        self.assertTrue(hasattr(tc, '_stop_event'))

    def test_read_line_normal_input(self):
        tc = TelnetContainer(Mock(), Mock(), {'socket_timeout': 10}, Mock())
        tc.source = Mock()
        tc.source.recv = Mock(side_effect=[b'u', b's', b'e', b'r', b'\n'])
        tc.source.settimeout = Mock()

        line = tc._read_line()

        self.assertEqual(line, 'user')

    def test_read_line_strips_iac_sequences(self):
        tc = TelnetContainer(Mock(), Mock(), {'socket_timeout': 10}, Mock())
        tc.source = Mock()
        tc.source.recv = Mock(side_effect=[
            b'\xff',           # IAC marker
            b'\xfb\x01',       # Two-byte response (consumed by recv(2))
            b'u', b's', b'e', b'r', b'\n'
        ])
        tc.source.settimeout = Mock()

        line = tc._read_line()

        self.assertEqual(line, 'user')

    def test_do_login_logs_credentials(self):
        mock_db = Mock()
        mock_conn = Mock()
        tc = TelnetContainer(Mock(), mock_conn, {'socket_timeout': 10}, mock_db)
        tc.source = Mock()
        tc.source.recv = Mock(side_effect=[
            b't', b'e', b's', b't', b'\n',
            b'p', b'a', b's', b's', b'\n'
        ])
        tc.source.sendall = Mock()
        tc.source.settimeout = Mock()

        tc._do_login()

        mock_db.write.assert_called_once()
        call_arg = mock_db.write.call_args[0][0]
        self.assertIsInstance(call_arg, tables.Credentials)
        self.assertEqual(call_arg.username, 'test')
        self.assertEqual(call_arg.password, 'pass')
        self.assertIs(call_arg.connection, mock_conn)

    def test_shutdown_stops_container(self):
        tc = TelnetContainer(Mock(), Mock(),
                             {'container': 'debian:bookworm-slim'}, Mock())
        tc.container = Mock()
        tc.source = Mock()

        tc.shutdown()

        self.assertTrue(tc._stop_event.is_set())
        tc.container.stop.assert_called_once()
        tc.container.remove.assert_called_once()

    def test_shutdown_handles_missing_resources(self):
        tc = TelnetContainer(Mock(), Mock(),
                             {'container': 'debian:bookworm-slim'}, Mock())
        tc.source = Mock()

        tc.shutdown()

        self.assertTrue(tc._stop_event.is_set())
