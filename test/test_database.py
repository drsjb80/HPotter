import unittest
from unittest.mock import patch, Mock

from src.database import Database
from src.tables import Base


class TestDatabase(unittest.TestCase):
    def test_get_database_string_default(self):
        db = Database({})
        s = db._get_database_string()
        self.assertTrue(s.startswith('sqlite:///'))

    def test_get_database_string_full(self):
        cfg = {
            'database': {
                'type': 'postgres',
                'user': 'u',
                'password': 'p',
                'host': 'h',
                'port': '5432',
                'name': 'n'
            }
        }
        db = Database(cfg)
        s = db._get_database_string()
        self.assertEqual(s, 'postgres://u:p@h:5432/n')

    def test_open_creates_engine_and_database(self):
        created = []

        class DummyEngine:
            def __init__(self, url):
                self.url = url

        with patch('src.database.create_engine', lambda x: DummyEngine(x)):
            with patch('src.database.database_exists', lambda url: False):
                with patch('src.database.create_database', lambda url: created.append(url)):
                    # patch metadata create_all to record call
                    with patch.object(Base.metadata, 'create_all') as mock_create:
                        cfg = {'database': {'type': 'sqlite', 'name': 'foo.db'}}
                        db = Database(cfg)
                        db.open()
                        self.assertIsNotNone(db.engine)
                        # engine.url should have been passed to create_database
                        self.assertEqual(created[0], db.engine.url)
                        mock_create.assert_called_with(db.engine)
