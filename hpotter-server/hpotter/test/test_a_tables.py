import unittest
from hpotter.tables import check_for_tables


class TestTables(unittest.TestCase):
    def test_checkTables(self):
        result = check_for_tables()
        if not result:
            check_again = check_for_tables()
            self.assertIsNotNone(check_again)
        else:
            self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
