import unittest
import os
# os.chdir("../../")
from hpotter.tables import checkForTables
from hpotter.env import Base, engine

class TestTables(unittest.TestCase):
    def test_checkTables(self):
        print('\nTesting for tables in main.db')
        result = checkForTables()
        if result == '1':
            #after we receive '1' the tables should be made and now return '5'
            self.assertEqual(checkForTables(), '5')
        else:
            self.assertEqual(result, '5')

if __name__ == '__main__':
    unittest.main()
