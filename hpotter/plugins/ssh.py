# from sqlalchemy import Column, String, Integer, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declared_attr
from hpotter.hpotter import HPotterDB
from hpotter.env import logger
import paramiko
import socket
import sys
import threading

from binascii import hexlify
from paramiko.py3compat import u, decodebytes

from sqlalchemy.orm import scoped_session

from hpotter.docker.shell import fake_shell
from hpotter.hpotter import consolidated
from hpotter.env import session_factory

class SSHServer(paramiko.ServerInterface):
    undertest = False    
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    def __init__(self, session, entry):
        self.event = threading.Event()
        self.session = session
        self.entry = entry

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # changed so that any username/password can be used
        if username and password:
            login = consolidated.LoginTable(username=username, password=password)
            login.hpotterdb = self.entry
            self.session.add(login)

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

def start_server():
    ssh_socket = socket.socket(socket.AF_INET)
    ssh_socket.bind(('0.0.0.0', 22))
    ssh_socket.listen(4)

    while True:
        client, addr = ssh_socket.accept()

        entry = HPotterDB.HPotterDB(
            sourceIP=addr[0],
            sourcePort=addr[1],
            destIP=ssh_socket.getsockname()[0],
            destPort=ssh_socket.getsockname()[1],
            proto=HPotterDB.TCP)

        transport = paramiko.Transport(client)
        transport.load_server_moduli()

        # Experiment with different key sizes at:
        # http://travistidwell.com/jsencrypt/demo/
        host_key = paramiko.RSAKey(filename="RSAKey.cfg")
        transport.add_server_key(host_key)

        session = scoped_session(session_factory)
        logger.info(session)
        server = SSHServer(session, entry)
        transport.start_server(server=server)
        chan = transport.accept()
        if not chan:
            print('no chan')
            continue

        fake_shell(chan, session, entry, '# ')
        chan.close()
        session.remove()

def stop_server():
    pass
