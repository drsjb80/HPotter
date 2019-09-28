import unittest
import os
# os.chdir("../../")
from hpotter.tables import checkForTables
from hpotter.env import Base, engine

class TestTables(unittest.TestCase):
    def test_checkTables(self):
        result = checkForTables()
        if not result:
            #after we receive '1' the tables should be made and now return '5'
            checkAgain = checkForTables()
            self.assertIsNotNone(checkAgain)
        else:
            self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
