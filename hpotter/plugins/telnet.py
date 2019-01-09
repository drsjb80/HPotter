from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger, Session
from hpotter.hpotter.command_response import command_response
from hpotter.hpotter import consolidated

import docker
import socket
import socketserver
import threading
import re

_shell_container = None
_telnet_server = None
busybox = True

# https://docs.python.org/3/library/socketserver.html
class TelnetHandler(socketserver.BaseRequestHandler):

    def setup(self):
        pass

    def get_string(self, socket, limit=4096, telnet=False):
        character = socket.recv(1)

        # while there are telnet commands
        while telnet and character == b'\xff':
            # skip the next two as they are part of the telnet command
            socket.recv(1)
            socket.recv(1)
            character = socket.recv(1)

        string = ''
        while character != b'\n' and character != b'\r':
            if character == b'\b':      # backspace
                string = string[:-1]
            elif character == '\x15':   # control-u
                string = ''
            elif ord(character) > 127 or ord(character) < 32:
                raise UnicodeError('control character')
            elif len(string) > limit:
                raise IOError('too many characters')
            else:
                string += character.decode('utf-8')

            character = socket.recv(1)

        # read the newline
        if character == b'\r':
            character = socket.recv(1)

        return string.strip()

    # leave this in telnet
    def creds(self, prompt, socket):
        tries = 0
        response = ''
        while response == '':
            socket.sendall(prompt)

            response = self.get_string(socket, limit=256, telnet=True)

            tries += 1
            if tries > 3:
                raise IOError('no response')

        return response

    def fake_shell(self, socket, entry, prompt):
        command_count = 0
        workdir = ''
        while command_count < 4:
            socket.sendall(prompt)

            try:
                command = self.get_string(socket)
                command_count += 1
            except:
                socket.close()
                break

            if command == '':
                continue

            if command.startswith('cd'):
                directory = command.split(' ')
                if len(directory) == 1:
                    continue

                directory = directory[1]

                if directory == '.':
                    continue

                if directory == '..':
                    workdir = re.sub(r'/[^/]*/?$', '', workdir)
                    continue

                if directory[0] != '/':
                    workdir += '/'
                workdir += directory

                continue

            if command == 'exit':
                break

            cmd = consolidated.CommandTable(command=command)
            cmd.hpotterdb = entry
            Session.add(cmd)

            global _shell_container
            timeout = 'timeout 1 ' if busybox else 'timeout -t 1 '
            exit_code, output = _shell_container.exec_run(timeout + command,
                workdir=workdir)

            if exit_code == 126:
                socket.sendall(command.encode('utf-8') + 
                    b': command not found\n')
            else:
                socket.sendall(output)

    def handle(self):
        entry = HPotterDB.HPotterDB(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.mysocket.getsockname()[0],
            destPort=self.server.mysocket.getsockname()[1],
            proto=HPotterDB.TCP)

        threading.Timer(120, self.request.close).start()

        try:
            username = self.creds(b'Username: ', self.request)
            password = self.creds(b'Password: ', self.request)
        except:
            return

        login = consolidated.LoginTable(username=username, password=password)
        login.hpotterdb = entry
        Session.add(login)

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\n')

        prompt = b'\n$: ' if username == 'root' or username == 'admin' else b'\n#: '
        
        self.fake_shell(self.request, entry, prompt)

    def finish(self):
        Session.commit()
        Session.remove()

# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class TelnetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, mysocket):
        # save socket for use in server_bind and handler
        self.mysocket = mysocket

        # must be called after setting mysocket as __init__ calls server_bind
        socketserver.TCPServer.__init__(self, None, TelnetHandler)

    def server_bind(self):
        self.socket = self.mysocket

# listen to both IPv4 and v6
# quad 0 allows for docker port exposure
def get_addresses():
    return [(socket.AF_INET, '0.0.0.0', 23)]

def start_server(my_socket):
    Session()

    client = docker.from_env()

    # move to main
    global _shell_container
    if busybox:
        _shell_container = client.containers.run('busybox', 
            command=['/bin/ash'], tty=True, detach=True, read_only=True)
    else:
        _shell_container = client.containers.run('busybox',
            command=['/bin/ash'], user='guest', tty=True, detach=True,
            read_only=True)

    network = client.networks.get('bridge')
    network.disconnect(_shell_container)

    global _telnet_server
    _telnet_server = TelnetServer(my_socket)
    server_thread = threading.Thread(target=_telnet_server.serve_forever)
    server_thread.start()

def stop_server():
    logger.info('Shutting down telnet server')
    _telnet_server.shutdown()
    # move these to main
    _shell_container.stop()
    _shell_container.remove()
    logger.info('Done shutting down telnet server')
