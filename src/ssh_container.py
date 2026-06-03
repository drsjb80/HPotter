'''SSH honeypot handler that accepts all login attempts and proxies shell sessions.'''

import threading
import docker
import paramiko

from src import tables
from src.container import Container
from src.lazy_init import lazy_init
from src.logger import logger

SSH_HOST_KEY = paramiko.RSAKey.generate(2048)


class SSHServer(paramiko.ServerInterface):
    '''Paramiko SSH server that accepts all logins and stores credentials.'''

    def __init__(self, connection, database):
        self.connection = connection
        self.database = database

    def check_auth_password(self, username, password):
        logger.info('SSH auth attempt: user=%s', username)
        self.database.write(
            tables.Credentials(
                username=username,
                password=password,
                connection=self.connection
            )
        )
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        return True


class SSHContainer(Container):
    '''SSH-based container handler.'''

    @lazy_init
    def __init__(self, source, connection, container_config, database):
        # Initialize parent class attributes via lazy_init-compat pattern
        self.container_ip = self.container_port = self.container_protocol = None
        self.dest = self.thread1 = self.thread2 = self.container = None
        self.transport = None
        self._stop_event = threading.Event()

    def run(self):
        client = None
        try:
            client = docker.from_env()
            logger.debug("created %s", client)
            self.container = client.containers.run(
                self.container_config['container'],
                detach=True,
                command='sleep infinity'
            )
            logger.info('SSH container started: %s', self.container.id[:12])

            self.transport = paramiko.Transport(self.source)
            self.transport.add_server_key(SSH_HOST_KEY)

            server = SSHServer(self.connection, self.database)
            try:
                self.transport.start_server(server=server)
            except paramiko.SSHException as exc:
                logger.info('SSH negotiation failed: %s', exc)
                return

            channel = self.transport.accept(20)
            if channel is None:
                logger.info('SSH: no channel opened within timeout')
                return

            self._bridge_channel(channel)

        except Exception as exc:
            logger.warning('SSHContainer error: %s', exc)
        finally:
            self._cleanup()

    def _bridge_channel(self, channel):
        api = docker.from_env().api
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

        # Handle urllib3 wrapper on the socket
        raw = getattr(exec_sock, '_sock', exec_sock)

        request_data = b''
        response_data = b''

        def container_to_channel():
            nonlocal response_data
            try:
                while not self._stop_event.is_set():
                    data = raw.recv(1024)
                    if not data:
                        break
                    response_data += data
                    channel.send(data)
            except Exception as exc:
                logger.debug('container->channel bridge ended: %s', exc)
            finally:
                channel.close()

        bridge_thread = threading.Thread(
            target=container_to_channel, daemon=True)
        bridge_thread.start()

        try:
            timeout = self.container_config.get('socket_timeout', 10)
            channel.settimeout(timeout)
            while not self._stop_event.is_set():
                try:
                    data = channel.recv(1024)
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
            try:
                channel.close()
            except Exception:
                pass

            # Save captured data if configured
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

    def _cleanup(self):
        if self.transport:
            try:
                self.transport.close()
            except Exception:
                pass
        if self.container:
            try:
                logger.info('Stopping SSH container %s', self.container.id[:12])
                self.container.stop()
                self.container.remove()
            except Exception as exc:
                logger.debug('Error stopping SSH container: %s', exc)
        try:
            self.source.close()
        except Exception:
            pass

    def shutdown(self):
        '''Shut down the SSH session and container.'''
        self._stop_event.set()
        if self.transport:
            try:
                self.transport.close()
            except Exception:
                pass
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
            except Exception:
                pass
