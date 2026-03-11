import socket
import ssl
import unittest
from unittest.mock import Mock

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
        sigalg = cert.get_signature_algorithm()
        if isinstance(sigalg, bytes):
            sigalg = sigalg.decode('ascii', 'ignore')
        sigalg = sigalg.lower()
        self.assertIn('sha256', sigalg)

        # subjectAltName extension must be present and include hostname
        host = socket.gethostname()
        san_found = False
        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name().decode() == 'subjectAltName':
                san_found = True
                self.assertIn(host, ext.__str__())
        self.assertTrue(san_found, "subjectAltName extension not added")

    def test_context_hardened(self):
        # the SSLContext created for TLS should have our hardened options set
        self.lt._gen_cert()
        ctx = self.lt.context
        # SSLv3 (and optionally TLS1.0/1.1) should be disabled
        self.assertTrue(ctx.options & ssl.OP_NO_SSLv3)
        self.assertTrue(ctx.options & ssl.OP_NO_TLSv1)
        # cipher list should contain HIGH and not aNULL or MD5
        ciphers = ctx.get_ciphers()
        cipher_names = {c['name'] for c in ciphers}
        self.assertTrue(any('AES' in name or 'CHACHA' in name for name in cipher_names))
