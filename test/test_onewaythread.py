import sys
import types
import unittest
from unittest.mock import Mock, call

# Create a dummy tables module so importing OneWayThread doesn't fail.
# This must be done before importing OneWayThread.
fake_tables = types.SimpleNamespace()
fake_tables.Data = object
sys.modules['src.tables'] = fake_tables

from src.one_way_thread import OneWayThread  # noqa: E402


class TestOneWayThread(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # pylint: disable=R0201
    def test_single(self):
        request = Mock()
        request.recv.side_effect = [bytes(i, 'utf-8') for i in 'a']
        response = Mock()

        connection = Mock()
        db = Mock()
        db.get_session = Mock(return_value=None)
        OneWayThread(request, response, connection, {}, 'request', db).run()

        response.sendall.assert_has_calls([call(b'a')])
        response.sendall.assert_called_once()

    def test_limit(self):
        request = Mock()
        request.recv.side_effect = [bytes(i, 'utf-8') for i in 'aaaa']
        response = Mock()

        db = Mock()
        connection = Mock()
        OneWayThread(request, response, connection, {'request_length': 2}, 'request', db).run()
        # since saving is disabled by default, db.write shouldn't be called
        assert not db.write.called

        response.sendall.assert_has_calls([call(b'a')], [call(b'a')])
        assert response.sendall.call_count == 2

