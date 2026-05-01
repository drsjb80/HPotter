import unittest

from src.lazy_init import lazy_init


class TestLazyInit(unittest.TestCase):
    def test_assigns_attributes(self):
        class Foo:
            @lazy_init
            def __init__(self, a, b=2, *args, **kwargs):
                # original constructor does nothing
                pass

        f = Foo(1, b=3, extra='x')
        self.assertEqual(f.a, 1)
        self.assertEqual(f.b, 3)
        # keyword args should also be set
        self.assertEqual(f.extra, 'x')

    def test_positional_binding(self):
        class Bar:
            @lazy_init
            def __init__(self, x, y, z=0):
                pass

        b = Bar(5, 6)
        self.assertEqual(b.x, 5)
        self.assertEqual(b.y, 6)
        self.assertEqual(b.z, 0)
