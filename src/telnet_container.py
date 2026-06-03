'''Telnet honeypot handler that accepts all login attempts and proxies shell sessions.'''

import threading
import docker

from src import tables
from src.container import Container
from src.lazy_init import lazy_init
from src.logger import logger


class TelnetContainer(Container):
    '''Telnet-based container handler.'''

    @lazy_init
    def __init__(self, source, connection, container_config, database):
        self.container_ip = self.container_port = self.container_protocol = None
        self.dest = self.thread1 = self.thread2 = self.container = None
        self._stop_event = threading.Event()

    def run(self):
        client = None
        try:
            client = docker.from_env()
            logger.debug("created %s", client)
            self.container = client.containers.run(
                self.container_config['container'],
                detach=True,
                command='sleep infinity',
                network_mode='none'
            )
            logger.info('Telnet container started: %s', self.container.id[:12])

            self._do_login()
            self._bridge_shell()

        except Exception as exc:
            logger.warning('TelnetContainer error: %s', exc)
        finally:
            self._cleanup()

    def _read_line(self):
        '''Read a line from the telnet client, stripping IAC option-negotiation bytes.

        Telnet clients emit IAC (0xff) sequences for option negotiation.
        We consume those silently and return the actual user input.
        '''
        buf = b''
        timeout = self.container_config.get('socket_timeout', 10)
        self.source.settimeout(timeout)

        while True:
            byte = self.source.recv(1)
            if not byte:
                break
            if byte == b'\xff':
                self.source.recv(2)
                continue
            if byte == b'\r' or byte == b'\n':
                if buf:
                    break
                continue
            buf += byte

        return buf.decode('utf-8', errors='replace')

    def _do_login(self):
        '''Send login and password prompts, capture credentials, log to DB.'''
        self.source.sendall(b'login: ')
        username = self._read_line()

        self.source.sendall(b'Password: ')
        password = self._read_line()

        logger.info('Telnet auth: user=%s', username)
        self.database.write(
            tables.Credentials(
                username=username,
                password=password,
                connection=self.connection
            )
        )

        self.source.sendall(b'\r\n')
        return username

    def _bridge_shell(self):
        '''Bridge telnet client socket to docker exec bash shell.'''
        client = None
        try:
            client = docker.from_env()
            api = client.api
            exec_id = api.exec_create(
                self.container.id,
                cmd=self.container_config.get('shell', '/bin/bash'),
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True
            )
            exec_sock = api.exec_start(
                exec_id['Id'],
                detach=False,
                tty=True,
                socket=True
            )

            raw = getattr(exec_sock, '_sock', exec_sock)

            request_data = b''
            response_data = b''

            def container_to_client():
                nonlocal response_data
                try:
                    while not self._stop_event.is_set():
                        data = raw.recv(1024)
                        if not data:
                            break
                        response_data += data
                        self.source.sendall(data)
                except Exception as exc:
                    logger.debug('container->client bridge ended: %s', exc)
                finally:
                    try:
                        self.source.close()
                    except Exception:
                        pass

            bridge_thread = threading.Thread(
                target=container_to_client, daemon=True)
            bridge_thread.start()

            try:
                timeout = self.container_config.get('socket_timeout', 10)
                self.source.settimeout(timeout)
                while not self._stop_event.is_set():
                    try:
                        data = self.source.recv(1024)
                    except Exception:
                        data = None
                    if not data:
                        break
                    request_data += data
                    raw.sendall(data)
            finally:
                self._stop_event.set()
                try:
                    raw.close()
                except Exception:
                    pass
                bridge_thread.join(timeout=5)

                if self.container_config.get('request_save', True) and request_data:
                    self.database.write(tables.Data(
                        direction='request',
                        data=str(request_data),
                        connection=self.connection
                    ))
                if self.container_config.get('response_save', False) and response_data:
                    self.database.write(tables.Data(
                        direction='response',
                        data=str(response_data),
                        connection=self.connection
                    ))
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

    def _cleanup(self):
        if self.container:
            try:
                logger.info('Stopping telnet container %s', self.container.id[:12])
                self.container.stop()
                self.container.remove()
            except Exception as exc:
                logger.debug('Error stopping telnet container: %s', exc)
        try:
            self.source.close()
        except Exception:
            pass

    def shutdown(self):
        '''Shut down the telnet session and container.'''
        self._stop_event.set()
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
            except Exception:
                pass
