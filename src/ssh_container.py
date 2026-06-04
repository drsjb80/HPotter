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
    '''Paramiko SSH server that accepts all logins and stores credentials.

    A honeypot server that logs all authentication attempts regardless of
    validity, then allows the attacker to proceed with a shell session.
    '''

    def __init__(self, connection, database):
        self.connection = connection
        self.database = database

    def check_auth_password(self, username, password):
        # Log all password auth attempts to the database, then accept them all
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
        # Only allow session channels (shell/exec), reject other types like SFTP
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        # Allow PTY allocation so interactive shells work properly
        return True

    def check_channel_shell_request(self, channel):
        # Allow shell requests
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
        # Main entry point: set up SSH transport, negotiate, accept shell channel,
        # then bridge it to a container shell session
        client = None
        try:
            client = docker.from_env()
            logger.debug("created %s", client)
            # network_mode='none' isolates the container to prevent pivot attacks
            self.container = client.containers.run(
                self.container_config['container'],
                detach=True,
                command='sleep infinity',
                network_mode='none'
            )
            logger.info('SSH container started: %s', self.container.id[:12])

            # Set up SSH server on the attacker's socket
            self.transport = paramiko.Transport(self.source)
            self.transport.add_server_key(SSH_HOST_KEY)

            server = SSHServer(self.connection, self.database)
            try:
                self.transport.start_server(server=server)
            except paramiko.SSHException as exc:
                logger.info('SSH negotiation failed: %s', exc)
                return

            # Wait for the attacker to request a channel (up to 20 seconds)
            channel = self.transport.accept(20)
            if channel is None:
                logger.info('SSH: no channel opened within timeout')
                return

            # Bridge the SSH channel to the container's shell
            self._bridge_channel(channel)

        except Exception as exc:
            logger.warning('SSHContainer error: %s', exc)
        finally:
            self._cleanup()

    def _bridge_channel(self, channel):
        # Bridge an SSH channel to a container's shell via bidirectional proxying.
        # Two threads handle data flow: one reads from the attacker's channel and
        # forwards to the container, another reads from the container and forwards
        # to the attacker's channel. They run concurrently to provide full-duplex.
        client = None
        try:
            client = docker.from_env()
            api = client.api
            # Create a shell execution session in the container
            exec_id = api.exec_create(
                self.container.id,
                cmd=self.container_config.get('shell', '/bin/bash'),
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True
            )
            # Start the shell and get a bidirectional socket to it
            exec_sock = api.exec_start(
                exec_id['Id'],
                detach=False,
                tty=True,
                socket=True
            )

            # docker.api.exec_start returns a urllib3 HTTPResponse wrapper;
            # unwrap it to get the raw socket for direct I/O
            raw = getattr(exec_sock, '_sock', exec_sock)

            # Accumulate traffic for optional logging
            request_data = b''
            response_data = b''

            def container_to_channel():
                # Read from container shell, forward to SSH client
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

            # Start the daemon thread that reads from the container
            bridge_thread = threading.Thread(
                target=container_to_channel, daemon=True)
            bridge_thread.start()

            try:
                timeout = self.container_config.get('socket_timeout', 10)
                channel.settimeout(timeout)
                # Main thread: read from SSH client, forward to container shell
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
                # Signal the other thread to stop
                self._stop_event.set()
                try:
                    raw.close()
                except Exception:
                    pass
                # Wait for the background thread to finish (up to 5 seconds)
                bridge_thread.join(timeout=5)
                try:
                    channel.close()
                except Exception:
                    pass

                # Save captured traffic to database if configured
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
        # Clean up all resources: SSH transport, Docker container, and client socket.
        # Called both during normal exit and error paths.
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
