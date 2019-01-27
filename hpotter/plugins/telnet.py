from hpotter.hpotter import tables
from hpotter.env import logger, Session, startShell, stopShell
from hpotter.docker.shell import fake_shell, get_string

import platform
import docker

import socket
import socketserver
import threading
import _thread
import re
# import pdb

telnet_server = None

# https://docs.python.org/3/library/socketserver.html
class TelnetHandler(socketserver.BaseRequestHandler):

    def creds(self, prompt, socket):
        tries = 0
        response = ''
        while response == '':
            socket.sendall(prompt)

            # pdb.set_trace()
            response = get_string(socket, limit=256, telnet=True)

            tries += 1
            if tries > 3:
                raise IOError('no response')

        return response

    def times_up(self):
        logger.info('Thread timed out')
        self.finish()
        self.request.close()
        _thread.exit()

    def handle(self):
        self.session = Session()
        entry = tables.ConnectionTable(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.socket.getsockname()[0],
            destPort=self.server.socket.getsockname()[1],
            proto=tables.TCP)

        threading.Timer(120, self.times_up).start()

        try:
            username = self.creds(b'Username: ', self.request)
            password = self.creds(b'Password: ', self.request)
        except:
            return

        login = tables.LoginTable(username=username, password=password)
        login.connectiontable = entry
        self.session.add(login)
        self.session.commit()

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\n')

        prompt = b'\n$: ' if username=='root' or username=='admin' else b'\n#: '
        fake_shell(self.request, self.session, entry, prompt, telnet=True)

    def finish(self):
        Session.remove()

class TelnetServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

def start_server():
    global telnet_server
    telnet_server = TelnetServer(('0.0.0.0', 23), TelnetHandler)
    server_thread = threading.Thread(target=telnet_server.serve_forever)
    server_thread.start()

def stop_server():
    logger.info('Shutting down telnet server')

    '''
    # https://github.com/python/cpython/blob/master/Lib/socketserver.py
    # shutdown() breaks out of the server_forever loop, checks every half a
    # second. well, it should but i can't make it work -- it blocks
    # forever. it doesn't seem to have to do with not having separate
    # threads, but needs looking into.
    logger.info('Calling shutdown')
    telnet_server.shutdown()
    '''

    # server_close() calls socket.close()
    # logger.info('Calling server_close')
    telnet_server.server_close()

    logger.info('Done shutting down telnet server')
