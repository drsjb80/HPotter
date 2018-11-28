from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
from hpotter.hpotter.command_response import command_response
from hpotter.hpotter import consolidated
import socket
import socketserver
import threading
import unittest
from unittest.mock import Mock, call
from hpotter.docker import linux_container


# Remember to put name in __init__.py

# https://docs.python.org/3/library/socketserver.html
class TelnetHandler(socketserver.BaseRequestHandler):
    undertest = False

    def setup(self):
        session = sessionmaker(bind=self.server.engine)
        self.session = session()

    def get_string(self, socket):
        character = socket.recv(1)

        # while there are telnet commands
        while character == b'\xff':
            # skip the next two as they are part of the telnet command
            socket.recv(1)
            socket.recv(1)
            character = socket.recv(1)

        string = ""
        while character != b'\n' and character != b'\r':
            if character == b'\b':
                string = string[:-1]
            else:
                string += character.decode("utf-8")
            character = socket.recv(1)

        # read the newline
        if character == b'\r':
            character = socket.recv(1)

        return string.strip()

    def trying(self, prompt, socket):
        tries = 0
        response = ''
        while response == '':
            socket.sendall(prompt)
            response = self.get_string(socket)
            tries += 1
            if tries > 3:
                return ''

        return response

    def fake_shell(self, socket, session, entry, prompt):
        command, work_dir, cd = "", "base", "cd"
        command_count = 0
        while command_count < 4:
            socket.sendall(prompt)
            command = self.get_string(socket)
            command_count += 1

            if command == '':
                continue
            elif command.startswith(cd):
                work_dir, dne = linux_container.change_directories(command)
                if dne is True:
                    dne_output = "\r\nbash: {}: command not found".format(command)
                    socket.sendall(dne_output.encode("utf-8"))
            elif command == 'exit':
                break
            elif command in command_response:
                socket.sendall(command_response[command].encode("utf-8"))
            else:
                output = "\r\n" + linux_container.get_response(command, work_dir)
                socket.sendall(output.encode("utf-8"))

            cmd = consolidated.CommandTable(command=command)
            cmd.hpotterdb = entry
            self.session.add(cmd)

    def handle(self):
        entry = HPotterDB.HPotterDB(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.mysocket.getsockname()[0],
            destPort=self.server.mysocket.getsockname()[1],
            proto=HPotterDB.TCP)

        username = self.trying(b'Username: ', self.request)
        if username == '':
            return

        prompt = b'\r\n#: '
        if username == 'root' or username == 'admin':
            prompt = b'\r\n$: '

        password = self.trying(b'Password: ', self.request)
        if password == '':
            return

        login = consolidated.LoginTable(username=username, password=password)
        login.hpotterdb = entry
        self.session.add(login)

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\r\n')
        
        self.fake_shell(self.request, self.session, entry, prompt)

    def finish(self):
        # ugly ugly ugly
        # i need to figure out how to properly mock sessionmaker
        if not self.undertest:
            self.session.commit()
            self.session.close()


# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
# http://stackoverflow.com/questions/8549177/is-there-a-way-for-baserequesthandler-classes-to-be-statful

class TelnetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, mysocket, engine):
        # save socket for use in server_bind and handler
        self.mysocket = mysocket

        # save engine for creating sessions in the handler
        self.engine = engine

        # must be called after setting mysocket as __init__ calls server_bind
        socketserver.TCPServer.__init__(self, None, TelnetHandler)

    def server_bind(self):
        self.socket = self.mysocket


# listen to both IPv4 and v6
# quad 0 allows for docker port exposure
def get_addresses():
    return [(socket.AF_INET, '0.0.0.0', 23)]


def start_server(my_socket, engine):
    server = TelnetServer(my_socket, engine)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
