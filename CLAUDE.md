# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HPotter is a honeypot. It listens on configured ports, and for each incoming
connection it spins up a throwaway Docker container running a real service
(httpd, telnet, etc.), then proxies bytes between the attacker and that
container while logging connection metadata and (optionally) the traffic to a
database. Each connection gets its own fresh container, which is stopped and
removed when the connection ends.

## Commands

The project uses a checked-in virtualenv at `venv/`. Activate it first:

```bash
source venv/bin/activate
pip install -r requirements.txt     # core deps; Docker daemon must be running
```

Run the honeypot (reads `config.yml` and `containers.yml` by default):

```bash
sudo python3 -m src
# or, after `setcap cap_net_bind_service` on the python binary, without sudo:
python3 -m src
# override config sources (both flags are append-style, repeatable):
python3 -m src --config config.yml --container containers.yml --loglevel debug
```

Tests are plain `unittest.TestCase` classes under `test/`, runnable with
either `pytest` (preferred) or the stdlib runner:

```bash
python3 -m pytest                               # all tests
python3 -m pytest test/test_listen_thread.py    # one module
python3 -m pytest test/test_listen_thread.py -k test_remote_ip_check  # one test
python3 -m unittest discover -s test            # stdlib equivalent
```

The metrics tests self-skip when `prometheus_client` is not installed (it's an
optional dependency). Everything else should pass; `geoip2` (listed in
`requirements.txt`) must be installed or `test_listen_thread.py` fails to
import.

Optional extras: `prometheus_client` (metrics on port 8000, see
`prometheus.yml`) and `geoip2` + a `GeoLite2/GeoLite2-City.mmdb` file (source
IP geolocation). Both degrade gracefully to disabled when absent.

## Architecture: the connection lifecycle

The threading model is the core of the design. Follow one connection through:

1. **`src/__main__.py` → `src/app.py:main`** — parses args, builds `HP`,
   calls `startup()`, then blocks on a `threading.Event` until SIGINT/SIGTERM
   (`GracefulKiller` sets the event), then `shutdown()`.

2. **`HP.startup`** — loads `config.yml` (single YAML doc, DB settings),
   opens the `Database`, optionally starts the Prometheus HTTP server, then
   for each YAML doc in `containers.yml` (multi-doc via `safe_load_all`)
   creates and `.start()`s a `ListenThread`.

3. **`src/listen_thread.py:ListenThread`** (a `threading.Thread`) — binds one
   socket on `listen_port`, accepts in a loop with a 5s timeout so it can
   notice `shutdown_requested`. Per accepted connection it: optionally wraps
   the socket in TLS (`_gen_cert` builds a hardened self-signed cert via the
   `cryptography` lib at startup), writes a `Connections` row (with geolocation
   if available), and submits a `ContainerThread.run` to a
   `ThreadPoolExecutor`. `container_list` tracks (future, thread) pairs and is
   pruned/used for shutdown.

4. **`src/container_thread.py:ContainerThread`** — a plain class (NOT a Thread;
   its `run` is submitted to the executor). It launches a Docker container via
   `docker.from_env()`, discovers the container's bridge IP/port, retries the
   socket connection up to ~10×, then starts two `OneWayThread`s and joins
   them. Cleans up the container (stop + remove) and all sockets in `finally`.

5. **`src/one_way_thread.py:OneWayThread`** (a `threading.Thread`) — proxies
   bytes in ONE direction. Two are created per connection: `request`
   (client→container) and `response` (container→client). Each enforces
   configurable limits: `{direction}_length` (max bytes), `{direction}_commands`
   (max delimiter-separated commands), `socket_timeout`. The `response` thread
   takes a `remote_ip` and refuses to write if the destination peer doesn't
   match (anti-redirection check). Traffic is saved to the `Data` table only
   when `{direction}_save` is set.

### Supporting modules

- **`src/database.py:Database`** — SQLAlchemy engine. `write()` serializes ALL
  writes through a single `threading.Lock` (required for SQLite under the
  multi-threaded model above). Defaults to `sqlite:///hpotter.db`; other
  backends are built from the `database:` block in `config.yml`.
- **`src/tables.py`** — SQLAlchemy ORM models: `Connections`, `Credentials`,
  `Data`. Table names are auto-derived as the lowercased class name.
- **`src/lazy_init.py:lazy_init`** — decorator on several `__init__` methods
  that auto-assigns constructor args to `self.<argname>`. If you read an
  `__init__` and don't see `self.foo = foo`, this decorator is why `self.foo`
  exists.
- **`src/metrics.py`** — Prometheus counters/gauges, with `_DummyMetric` no-op
  fallbacks when `prometheus_client` is missing.
- **`src/logger.py` / `src/logging.conf`** — shared `hpotter` logger; level is
  overridden at runtime by `--loglevel`.

## Configuration

- **`config.yml`** — global settings, primarily the `database:` block. Loaded
  as a single document.
- **`containers.yml`** — one YAML document PER listener. Keys include
  `container` (Docker image), `listen_port`, `listen_address`, `TLS`,
  `request_save`/`response_save`, `socket_timeout`, the `*_length`/`*_commands`/
  `*_delimiters` limits, `threads` (executor pool size), and `arguments` (an
  `ast.literal_eval` string of kwargs passed to Docker). A `serial:` key, if
  present, is auto-incremented and rewritten on startup. See `README.md` for
  the full key list.
- **`telnet-debian/`** — Dockerfile for a one-shot Debian telnet target image
  used as a honeypot container.

## Conventions specific to this repo

- Don't busy-wait and avoid arbitrary timeouts where a blocking/event-driven
  approach works (see `CODING_PREFERENCES.md`); the accept loop's 5s timeout
  exists specifically to poll the shutdown flag.
- Sockets, Docker clients, and DB sessions must be closed in `finally` blocks —
  FD/container leaks are a recurring concern here.
- Outstanding TODO from `NOTES.md`: TLS policy is hardcoded in
  `listen_thread._harden`; exposing it via config was suggested but not done.
