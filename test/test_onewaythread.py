import unittest
from unittest.mock import call, patch, Mock
import sys, types

# create a dummy tables module so importing OneWayThread doesn't fail
fake_tables = types.SimpleNamespace()
# add minimal attributes that code might reference
fake_tables.Data = object
sys.modules['src.tables'] = fake_tables

from src.one_way_thread import OneWayThread
from src.lazy_init import lazy_init

# no real DB module available during tests; we'll just use mocks
# from src.db import DB

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

    def test_remote_ip_check(self):
        # when response thread sees a peer with wrong IP, the write should be
        # refused and the loop will exit without sending any data.
        request = Mock()
        request.recv.side_effect = [b'hello', b'']
        response = Mock()
        response.getpeername.return_value = ('10.0.0.5', 1234)

        connection = Mock()
        db = Mock()
        db.get_session = Mock(return_value=None)
        thread = OneWayThread(request, response, connection, {}, 'response', db,
                               remote_ip='1.2.3.4')
        thread.run()
        # the message should not have been forwarded
        response.sendall.assert_not_called()

