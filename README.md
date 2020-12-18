
# HPotter
A simple to install and run Honey Pot.

[![Build Status](https://travis-ci.org/drsjb80/HPotter.svg?branch=master)](https://travis-ci.org/drsjb80/HPotter)

## Running and developing

To install the necessary packages, do:

    pip install -r requirements.txt

To run the honeypot itself, do:

    python3 -m src

## Databases
The default database is SQLite and requires no configuration. The tables
are written into the default ("main.db") database.

If you'd like to use a different database, there are some environment
variables that need setting.

HPOTTER\_DB -- the name of the database type, e.g.: "mysql".
    Defaults to "sqlite".

HPOTTER\_DB\_PASSWORD -- e.g.: "my-secret-pw".
    Defaults to "".

HPOTTER\_DB\_HOST
    Defaults to "127.0.0.1".

HPOTTER\_DB\_PORT -- e.g.: 3306
    Defaults to "".

HPOTTER\_DB\_DB -- The database where the tables are placed e.g.: hpotter.
Created if not present.  Defaults to "hpotter".
