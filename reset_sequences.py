#!/usr/bin/env python3
"""Reset PostgreSQL sequences after data migration.

When migrating data from SQLite to PostgreSQL, the auto-increment sequences
need to be reset to start after the highest existing ID in each table.

Usage:
    python3 reset_sequences.py [--config config.yml]
"""

import argparse
import sys
from pathlib import Path

import yaml
from sqlalchemy import text

from src.database import Database
from src.logger import logger


def load_config(config_path='config.yml'):
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        logger.error(f'Config file not found: {config_path}')
        sys.exit(1)

    with open(config_file) as f:
        return yaml.safe_load(f)


def reset_sequences(db):
    """Reset all table sequences to start after the highest existing ID."""
    session = db.SessionLocal()
    tables = ['connections', 'credentials', 'data']

    try:
        for table in tables:
            # Get the max ID from the table
            result = session.execute(text(f'SELECT MAX(id) FROM {table}')).scalar()
            max_id = result if result is not None else 0
            next_id = max_id + 1

            # Reset the sequence
            sequence_name = f'{table}_id_seq'
            session.execute(text(f"SELECT setval('{sequence_name}', {next_id})"))
            logger.info(f'Reset {sequence_name} to start at {next_id}')

        session.commit()
        logger.info('All sequences reset successfully')
    except Exception as e:
        session.rollback()
        logger.error(f'Error resetting sequences: {e}')
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description='Reset PostgreSQL sequences after data migration'
    )
    parser.add_argument(
        '--config',
        default='config.yml',
        help='Path to config.yml (default: config.yml)'
    )
    args = parser.parse_args()

    logger.info(f'Loading config from {args.config}')
    config = load_config(args.config)

    logger.info('Connecting to database')
    db = Database(config)
    db.open()

    try:
        reset_sequences(db)
    finally:
        db.close()


if __name__ == '__main__':
    main()
