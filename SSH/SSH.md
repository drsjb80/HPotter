FROM debian:bookworm-slim
# Install only the system packages your application actually needs
RUN apt-get update && apt-get install -y curl procps && rm -rf /var/lib/apt/lists/*
CMD ["sleep", "infinity"]

docker build -t my-debian-app .
docker run -d --name target-debian-container my-debian-app

gateway.pl
import socket
import sys
import threading
import paramiko
import docker

# Generate or load host key
HOST_KEY = paramiko.RSAKey.generate(2048)

# Initialize Docker client using local unix socket
docker_client = docker.from_env()

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # Externalized authentication layer
        if username == "admin" and password == "password123":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_shell_request(self, channel):
        return True

    def check_pty_request(self, channel, term, width, height, pixelwidth, pixelheight):
        return True

def bridge_streams(channel, docker_socket):
    """Bridges data from Docker container output back to the Paramiko SSH channel."""
    try:
        while True:
            # Read from Docker raw stream socket
            data = docker_socket.read(1024)
            if not data:
                break
            channel.send(data)
    except Exception:
        pass
    finally:
        channel.close()

def handle_client(client_sock):
    transport = paramiko.Transport(client_sock)
    transport.add_server_key(HOST_KEY)

    server = Server()
    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        return

    channel = transport.accept(20)
    if channel is None:
        return

    try:
        # 1. Locate the running standalone container
        container = docker_client.containers.get("target-debian-container")

        # 2. Create an exec instance running bash with a TTY attached
        exec_instance = docker_client.api.exec_create(
            container.id,
            cmd="/bin/bash",
            stdin=True,
            stdout=True,
            stderr=True,
            tty=True
        )

        # 3. Open a raw socket connection to the exec stream
        # This returns a DockerExecSocket containing a file descriptor/socket
        exec_socket = docker_client.api.exec_start(exec_instance['Id'], detach=False, tty=True, stream=True)

        # 4. Spin up a thread to read container stdout -> send to SSH client
        thr = threading.Thread(target=bridge_streams, args=(channel, exec_socket.output))
        thr.daemon = True
        thr.start()

        # 5. Loop to read SSH client stdin -> write directly to the container socket
        while True:
            data = channel.recv(1024)
            if not data:
                break
            exec_socket.output.write(data)

    except Exception as e:
        print(f"Error bridging to container: {e}")
    finally:
        channel.close()
        transport.close()

def main():
    # Bind to host interface port 2222
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 2222))
    sock.listen(100)
    print("Paramiko gateway listening on port 2222...")

    try:
        while True:
            client_sock, addr = sock.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock,))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down gateway.")

if __name__ == "__main__":
    main()


Run python gateway.py on your host.
Run ssh admin@localhost -p 2222.
The script verifies credentials natively on the host machine.
If successful, it interacts with /var/run/docker.sock, executes /bin/bash dynamically inside target-debian-container, and feeds the terminal I/O down the SSH line.
If the user disconnects or types exit, the execution context dies inside the container, leaving the container clean and undisturbed.
