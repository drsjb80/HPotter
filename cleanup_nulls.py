#!/usr/bin/env python3
"""Clean null characters from database credentials.

PostgreSQL doesn't allow null characters in TEXT columns, but SQLite does.
This script removes null characters from usernames and passwords in the
Credentials table to ensure compatibility with PostgreSQL.

Usage:
    python3 cleanup_nulls.py [--config config.yml]
"""

import argparse
import sys
from pathlib import Path

import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.tables import Credentials
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


def cleanup_credentials(db):
    """Remove null characters from all credentials in the database."""
    session = db.SessionLocal()
    try:
        credentials = session.query(Credentials).all()
        cleaned_count = 0

        for cred in credentials:
            original_username = cred.username
            original_password = cred.password

            if cred.username and '\x00' in cred.username:
                cred.username = cred.username.replace('\x00', '')
                logger.debug(f'Cleaned null character from username: {repr(original_username)} -> {repr(cred.username)}')
                cleaned_count += 1

            if cred.password and '\x00' in cred.password:
                cred.password = cred.password.replace('\x00', '')
                logger.debug(f'Cleaned null character from password: {repr(original_password)} -> {repr(cred.password)}')
                cleaned_count += 1

        if cleaned_count > 0:
            session.commit()
            logger.info(f'Cleaned {cleaned_count} credential fields with null characters')
        else:
            logger.info('No null characters found in credentials')

        return cleaned_count
    except Exception as e:
        session.rollback()
        logger.error(f'Error during cleanup: {e}')
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description='Clean null characters from HPotter database credentials'
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
        logger.info('Starting null character cleanup')
        cleaned = cleanup_credentials(db)
        logger.info(f'Cleanup complete. {cleaned} fields cleaned.')
    finally:
        db.close()


if __name__ == '__main__':
    main()
