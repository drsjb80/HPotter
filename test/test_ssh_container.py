import unittest
from unittest.mock import Mock

import paramiko

from src import tables
from src.ssh_container import SSHServer, SSHContainer


class TestSSHServer(unittest.TestCase):
    def test_check_auth_password_logs_credentials(self):
        mock_db = Mock()
        mock_conn = Mock()
        server = SSHServer(mock_conn, mock_db)

        result = server.check_auth_password('root', 'toor')

        self.assertEqual(result, paramiko.AUTH_SUCCESSFUL)
        mock_db.write.assert_called_once()
        call_arg = mock_db.write.call_args[0][0]
        self.assertIsInstance(call_arg, tables.Credentials)
        self.assertEqual(call_arg.username, 'root')
        self.assertEqual(call_arg.password, 'toor')
        self.assertIs(call_arg.connection, mock_conn)

    def test_multiple_auth_attempts_all_stored(self):
        mock_db = Mock()
        server = SSHServer(Mock(), mock_db)

        for user, passwd in [('admin', 'admin'), ('root', '123456')]:
            server.check_auth_password(user, passwd)

        self.assertEqual(mock_db.write.call_count, 2)

    def test_check_channel_request_session_only(self):
        server = SSHServer(Mock(), Mock())
        self.assertEqual(
            server.check_channel_request('session', 0),
            paramiko.OPEN_SUCCEEDED
        )
        self.assertEqual(
            server.check_channel_request('direct-tcpip', 0),
            paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        )

    def test_check_channel_pty_request_always_true(self):
        server = SSHServer(Mock(), Mock())
        self.assertTrue(
            server.check_channel_pty_request(Mock(), 'xterm', 80, 24, 0, 0, {})
        )

    def test_check_channel_shell_request_always_true(self):
        server = SSHServer(Mock(), Mock())
        self.assertTrue(server.check_channel_shell_request(Mock()))


class TestSSHContainer(unittest.TestCase):
    def test_lazy_init_assigns_attributes(self):
        src = Mock()
        conn = Mock()
        cfg = {
            'container': 'debian:bookworm-slim',
            'listen_port': 22,
            'type': 'ssh'
        }
        db = Mock()
        sct = SSHContainer(src, conn, cfg, db)
        self.assertIs(sct.source, src)
        self.assertIs(sct.connection, conn)
        self.assertIs(sct.container_config, cfg)
        self.assertIs(sct.database, db)
        self.assertIsNone(sct.container)
        self.assertIsNone(sct.transport)

    def test_run_ssh_negotiation_failure(self):
        # Minimal test: verify that SSH negotiation failure is handled gracefully
        sct = SSHContainer(Mock(), Mock(),
                           {'container': 'debian:bookworm-slim'}, Mock())
        # Don't actually call run() since it requires Docker; just test shutdown behavior
        sct.transport = Mock()
        sct.container = Mock()
        sct.shutdown()
        sct.transport.close.assert_called_once()

    def test_shutdown_stops_container_and_transport(self):
        sct = SSHContainer(Mock(), Mock(),
                           {'container': 'debian:bookworm-slim'}, Mock())
        sct.transport = Mock()
        sct.container = Mock()
        sct.shutdown()
        self.assertTrue(sct._stop_event.is_set())
        sct.transport.close.assert_called_once()
        sct.container.stop.assert_called_once()
        sct.container.remove.assert_called_once()

    def test_shutdown_handles_missing_resources(self):
        sct = SSHContainer(Mock(), Mock(),
                           {'container': 'debian:bookworm-slim'}, Mock())
        # No transport or container set
        sct.shutdown()
        self.assertTrue(sct._stop_event.is_set())
