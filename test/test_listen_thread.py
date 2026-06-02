import geoip2.errors
import socket
import ssl
import unittest
from unittest.mock import Mock

from cryptography.x509.oid import ExtensionOID
from src.listen_thread import ListenThread


class TestListenThread(unittest.TestCase):
    def setUp(self):
        # the ListenThread constructor is decorated with lazy_init, so
        # attributes aren't set until first use; call run() or _gen_cert directly
        self.container = {'listen_port': 1234, 'TLS': True}
        self.lt = ListenThread(self.container, Mock())

    def test_gen_cert_contains_san_and_sha256(self):
        # generate a certificate and ensure it has the expected features
        self.lt._gen_cert()
        self.assertIsNotNone(self.lt.context)
        self.assertTrue(hasattr(self.lt, 'cert'), "generated cert should be stored")

        cert = self.lt.cert
        # certificate should be signed with a SHA-2 family digest
        sigalg = cert.signature_hash_algorithm.name
        self.assertIn('sha256', sigalg.lower())

        # subjectAltName extension must be present and include hostname
        san = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        host = socket.gethostname()
        self.assertIn(host, str(san.value))

    def test_context_hardened(self):
        # SSLContext created for TLS should have our hardened settings set
        self.lt._gen_cert()
        ctx = self.lt.context
        self.assertEqual(ctx.minimum_version, ssl.TLSVersion.TLSv1_2)
        self.assertEqual(ctx.maximum_version, ssl.TLSVersion.TLSv1_3)
        # cipher list should contain HIGH and not aNULL or MD5
        ciphers = ctx.get_ciphers()
        cipher_names = {c['name'] for c in ciphers}
        self.assertTrue(any('AES' in name or 'CHACHA' in name for name in cipher_names))

    def test_save_connection_basic(self):
        # verify that a connection record is created and written to the database
        # when geoip is disabled and no destination data is requested
        from src import listen_thread

        # disable geoip reader and patch Connections to simple namespace
        listen_thread.READER = False
        saved = {}
        class DummyConn:
            def __init__(self, **kwargs):
                saved.update(kwargs)
        listen_thread.tables.Connections = DummyConn

        db = Mock()
        lt = ListenThread({'listen_port': 1111, 'container': 'foo'}, db)
        lt._save_connection(('2.2.2.2', 4242))
        db.write.assert_called_once()
        # ensure required fields are preserved
        self.assertEqual(saved['source_address'], '2.2.2.2')
        self.assertEqual(saved['source_port'], 4242)
        self.assertEqual(saved['container'], 'foo')

    def test_save_connection_with_destination_and_geoip_error(self):
        # if save_destination is set and geoip lookup fails, destination fields
        # still appear and geoip fields are None
        from src import listen_thread
        class BadReader:
            def city(self, ip):
                raise geoip2.errors.AddressNotFoundError('address not found')
        listen_thread.READER = BadReader()
        # patch Connections again
        saved = {}
        class DummyConn2:
            def __init__(self, **kwargs):
                saved.update(kwargs)
        listen_thread.tables.Connections = DummyConn2

        db = Mock()
        lt = ListenThread({'listen_port': 2222, 'container': 'bar',
                           'save_destination': True,
                           'listen_address': '1.1.1.1',
                           'listen_port': 2222}, db)
        lt._save_connection(('5.5.5.5', 3333))
        db.write.assert_called_once()
        # destination fields included
        self.assertEqual(saved['destination_address'], '1.1.1.1')
        self.assertEqual(saved['destination_port'], 2222)
        # geoip fallback
        self.assertIsNone(saved.get('city'))
        self.assertIsNone(saved.get('latitude'))

    def test_create_listen_socket_sets_options(self):
        # patch socket.socket to inspect operations
        import src.listen_thread as lt_mod

        class FakeSock:
            def __init__(self):
                self.opts = []
                self.timeout = None
                self.bound = None
            def setsockopt(self, level, opt, val):
                self.opts.append((level, opt, val))
            def settimeout(self, t):
                self.timeout = t
            def bind(self, addr):
                self.bound = addr
            def listen(self):
                pass
            def close(self):
                pass
        orig_socket = lt_mod.socket.socket
        lt_mod.socket.socket = lambda *a, **k: FakeSock()
        lt = ListenThread({'listen_port': 3333, 'container': 'baz'}, Mock())
        sock = lt._create_listen_socket()
        self.assertEqual(sock.bound, ('', 3333))
        # ensure SO_REUSEADDR was set
        found = any(opt == socket.SO_REUSEADDR for (_, opt, _) in sock.opts)
        self.assertTrue(found)
        self.assertEqual(sock.timeout, 5)
        lt_mod.socket.socket = orig_socket

    def test_run_submits_handler_and_honours_shutdown(self):
        # simulate a single accept, then a timeout causing exit
        import src.listen_thread as lt_mod
        class DummySource:
            def __init__(self):
                self.timeout = None
            def settimeout(self, t):
                self.timeout = t
            def close(self):
                pass

        class DummySocket:
            def __init__(self):
                self.accept_calls = 0
                self.timeout = None
                self.bound = None
                self.opts = []
            def setsockopt(self, a, b, c):
                self.opts.append((a,b,c))
            def settimeout(self, t):
                self.timeout = t
            def bind(self, addr):
                self.bound = addr
            def listen(self):
                pass
            def accept(self):
                self.accept_calls += 1
                if self.accept_calls == 1:
                    return DummySource(), ('9.9.9.9', 9999)
                raise socket.timeout
            def close(self):
                pass
        class DummyExecutor:
            def __init__(self, max_workers=None):
                self.submitted = []
            def submit(self, fn, *args, **kwargs):
                self.submitted.append((fn, args, kwargs))
                f = Mock()
                f.running.return_value = False
                f.done.return_value = False
                return f
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        orig_socket = lt_mod.socket.socket
        orig_executor = lt_mod.ThreadPoolExecutor
        lt_mod.socket.socket = lambda *a, **k: DummySocket()
        lt_mod.ThreadPoolExecutor = DummyExecutor

        db = Mock()
        # force shutdown_requested true after first connection to break loop
        lt = ListenThread({'listen_port': 4444, 'container': 'qux'}, db)
        def make_shutdown(addr):
            lt.shutdown_requested = True
            return None
        lt._save_connection = make_shutdown
        lt.run()
        # verify executor got one submission
        self.assertEqual(len(lt.container_list), 1)
        fut, thread = lt.container_list[0]
        self.assertFalse(fut.running())

        lt_mod.socket.socket = orig_socket
        lt_mod.ThreadPoolExecutor = orig_executor

    def test_shutdown_method_calls_container_shutdown(self):
        lt = ListenThread({'listen_port': 5555, 'container': 'z'} , Mock())
        dummy_future = Mock()
        dummy_future.running.return_value = True
        dummy_thread = Mock()
        lt.container_list = [(dummy_future, dummy_thread)]
        lt.shutdown()
        dummy_thread.shutdown.assert_called_once()
        self.assertTrue(lt.shutdown_requested)

    def test_container_thread_shutdown_handles_missing_resources(self):
        from src.container_thread import ContainerThread

        ct = ContainerThread(Mock(), Mock(), Mock(), Mock())
        ct.thread1 = Mock()
        ct.thread2 = Mock()
        ct.dest = Mock()
        ct.container = None

        ct.shutdown()

        ct.thread1.shutdown.assert_called_once()
        ct.thread2.shutdown.assert_called_once()
        ct.dest.close.assert_called_once()

    def test_prune_completed_containers(self):
        lt = ListenThread({'listen_port': 5555, 'container': 'z'}, Mock())
        active_future = Mock()
        active_future.done.return_value = False
        finished_future = Mock()
        finished_future.done.return_value = True
        lt.container_list = [
            (active_future, Mock()),
            (finished_future, Mock()),
        ]
        lt._prune_completed_containers()
        self.assertEqual(len(lt.container_list), 1)
        self.assertIs(lt.container_list[0][0], active_future)

