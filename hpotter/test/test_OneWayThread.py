import unittest
from unittest.mock import call, patch
from hpotter.plugins.OneWayThread import OneWayThread
# from hpotter.plugins.telnet import start_server, stop_server
# from hpotter.env import start_shell, stop_shell

@patch('hpotter.db')
def write_db(arg):
    pass

class TestOneWayThread(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # pylint: disable=R0201
    def test_SendSingle(self):
        tosend = 'a'
        request = unittest.mock.Mock()
        request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]
        response = unittest.mock.Mock()

        owt = OneWayThread(request, response, {}, 'request')
        owt.run()

        response.sendall.assert_has_calls([call(b'a')])

    def test_TestLimit(self):
        tosend = 'aa'
        request = unittest.mock.Mock()
        request.recv.side_effect = [bytes(i, 'utf-8') for i in tosend]
        response = unittest.mock.Mock()

        owt = OneWayThread(request, response, {'request_length': 2}, 'request')
        owt.run()

        print(response.calls)
        response.sendall.assert_has_calls([call(b'a')])

