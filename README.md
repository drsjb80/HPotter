# HPotter
A simple to install and run Honey Pot.

[![CI / CD Pipeline](https://github.com/drsjb80/HPotter/actions/workflows/ci.yml/badge.svg)](https://github.com/drsjb80/HPotter/actions/workflows/ci.yml)


## Running and developing

Clone the repo

    git clone https://github.com/drsjb80/HPotter
    cd HPotter
    source venv/bin/activate

Make sure you're running Docker.

To install the necessary packages, do:

    pip install -r requirements.txt

Optional Prometheus metrics are supported if you also install `prometheus_client`. When available, metrics are exposed on port `8000`. See prometheus.yml for configuration. You'll need to so `sudo systemctl restart prometheus` and check via `sudo systemctl status  prometheus`.

Recommended: allow python3 to run on priviledged ports without sudo:

    sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.10

To run the honeypot itself, do:

    sudo python3 -m src

or, and recommended, if you've done the setcap:

    python3 -m src

This should create listeners for HTTP, HTTPS, and telnet. Point your local
broser to http://127.0.0.1 and https://127.0.0.1 For HTTPS, you'll need to
accept the risk (minimal in this case) and find one of the Easter Eggs.

### Database Configuration

By default, HPotter uses SQLite (`hpotter.db`). To use PostgreSQL or override database settings, set environment variables:

    export DB_TYPE=postgresql
    export DB_HOST=your-postgres-host.rds.amazonaws.com
    export DB_NAME=hpotter
    export DB_USER=hpotter
    export DB_PASSWORD=your_secure_password
    python3 -m src

Environment variables take precedence over `config.yml` values. This keeps credentials out of version control.

See `.env.example` for all available environment variables.

When/if you want to monitor who is probing you from the internet, you'll
need to create port forwarding on your DSL/Cable modem etc. Here's a screen
shot of how the might look for you.

![Port Fowarding](/IMG_2928.PNG)

### GeoIP
If you want to capture geoip information, you'll need to:

    pip install geoip2

and download `GeoLite2-City.mmdb` from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data/

### containers.yml
A list of one or more of the following.
* container, the name of the Docker container to run
* listen\_address, default: 0.0.0.0
* listen\_port, the port number.
* request\_length, how many bytes requests are allowed to be, default: 4096.
* response\_length, how many bytes responses are allowed to be, default: 4096.
* request\_commands, how many request commands (between delimiters), default: 10.
* response\_commands, how many response commands (between delimiters), default: 10.
* request\_delimiters, a list of delimiters between request commands, default: - \n\r.
* response\_delimiters, a list of delimiters between response commands, default: - \n\r.
* socket\_timeout, how many seconds of inactivity before closing socket. 
* threads, how many concurrent threads for this type of container, default: Python's default.
* arguments, takes a valid [ast.literal_eval](https://docs.python.org/3/library/ast.html#ast.literal_eval) input.
    * Example: 'arguments': '{"publish_all_ports":True, "detach":True, "volumes":["tmp:/tmp"]}'
### config.yml
* database, default: 'sqlite'
* database\_name, default: 'hpotter.db'
* database\_user, default: ''
* database\_password, default: ''
* database\_host, default: ''
* database\_port', default: ''

## Migrating from SQLite to PostgreSQL

If you have an existing HPotter database and want to migrate to PostgreSQL:

1. **Dump SQLite data** (use standard tools like `sqlite3` or a migration tool)

2. **Clean null characters** (PostgreSQL doesn't allow null bytes in TEXT columns):
   ```bash
   python3 cleanup_nulls.py
   ```

3. **Reset auto-increment sequences** (if you imported existing data):
   ```bash
   python3 reset_sequences.py
   ```

These scripts automatically use environment variables or `config.yml` for database configuration, the same as the main application.
