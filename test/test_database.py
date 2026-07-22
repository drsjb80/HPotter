import os
import unittest
from unittest.mock import patch

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

    def test_get_database_string_env_postgresql(self):
        cfg = {}
        with patch.dict(os.environ, {
            'DB_TYPE': 'postgresql',
            'DB_HOST': 'pghost',
            'DB_NAME': 'pgdb',
            'DB_USER': 'pguser',
            'DB_PASSWORD': 'pgpass',
            'DB_PORT': '5432'
        }):
            db = Database(cfg)
            s = db._get_database_string()
            self.assertEqual(s, 'postgresql://pguser:pgpass@pghost:5432/pgdb')

    def test_get_database_string_env_overrides_config(self):
        cfg = {
            'database': {
                'type': 'sqlite',
                'name': 'config.db'
            }
        }
        with patch.dict(os.environ, {
            'DB_TYPE': 'postgresql',
            'DB_NAME': 'envdb'
        }):
            db = Database(cfg)
            s = db._get_database_string()
            self.assertTrue(s.startswith('postgresql://'))
            self.assertIn('envdb', s)

    def test_get_database_string_env_sqlite(self):
        cfg = {}
        with patch.dict(os.environ, {
            'DB_TYPE': 'sqlite',
            'DB_NAME': 'test.db'
        }):
            db = Database(cfg)
            s = db._get_database_string()
            self.assertEqual(s, 'sqlite:///test.db')

    def test_get_database_string_env_partial_postgres(self):
        cfg = {}
        with patch.dict(os.environ, {
            'DB_TYPE': 'postgresql',
            'DB_HOST': 'pghost'
        }, clear=False):
            db = Database(cfg)
            s = db._get_database_string()
            self.assertTrue(s.startswith('postgresql://'))
            self.assertIn('@pghost', s)

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
