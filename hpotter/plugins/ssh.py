from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.hpotter.command_response import command_response
from paramiko.py3compat import u, decodebytes
from hpotter.hpotter import consolidated
import socket
import paramiko
import threading
from binascii import hexlify
import sys


class SSHServer(paramiko.ServerInterface):
    undertest = False    
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    def __init__(self, mysocket, addr):
        self.mysocket = mysocket
        self.addr = addr
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # changed so that any username/password can be used
        if username and password:
            self.entry = HPotterDB.HPotterDB(
                sourceIP=self.addr[0],
                sourcePort=self.addr[1],
                destIP=self.mysocket.getsockname()[0],
                destPort=self.mysocket.getsockname()[1],
                proto=HPotterDB.TCP)
            login = consolidated.LoginTable(username=username, password=password)
            login.hpotterdb = self.entry
            Session.add(login)

            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print("Auth attempt with key: " + u(hexlify(key.get_fingerprint())))
        if username == 'exit':
            sys.exit(1)
        if(username == "user") and (key == self.good_pub_key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    # Turned off, causing problems
    def enable_auth_gssapi(self):
        return False

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
            self, channel, term, width, height, pixelwidth, pixelheight,
            modes):
        return True

    # help from:
    # https://stackoverflow.com/questions/24125182/how-does-paramiko-channel-recv-exactly-work
    def receive_client_data(self, chan):
        command, work_dir, cd = "", "base", "cd"
        command_count = 0

        while True:
            character = chan.recv(1024).decode("utf-8")
            if character == ("\r" or "\r\n" or ""):
                if command.startswith(cd):
                    work_dir, dne = linux_container.change_directories(command)
                    if dne is True:
                        dne_output = "\r\nbash: {}: command not found".format(command)
                        chan.send(dne_output)
                elif command in command_response:
                    chan.send(command_response[command])
                else:
                    output = "\r\n" + linux_container.get_response(command, work_dir)
                    chan.send(output)

                cmd = consolidated.CommandTable(command=command)
                cmd.hpotterdb = self.entry
                Session.add(cmd)

                command_count += 1
                if command_count > 3 or command == "exit":
                    break
                command = ""
                chan.send("\r\n# ")
            else:
                command += character
                chan.send(character)

        Session.commit()
        Session.remove()

def start_server():
    socket = socket.socket(socket.AF_INET)
    socket.bind(('0.0.0.0', 22))
    socket.listen(4)

    while True:
        client, addr = socket.accept()

        transport = paramiko.Transport(client)
        transport.load_server_moduli()

        # Experiment with different key sizes at:
        # http://travistidwell.com/jsencrypt/demo/
        host_key = paramiko.RSAKey(filename="RSAKey.cfg")
        transport.add_server_key(host_key)

        server = SSHServer(socket, addr)
        transport.start_server(server=server)
        chan = transport.accept()
        if not chan:
            print('no chan')
            continue
        server.receive_client_data(chan)
        chan.close()

def stop_server():
    pass
