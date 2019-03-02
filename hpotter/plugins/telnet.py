import socketserver
import threading
import _thread

import hpotter.env

from hpotter import tables
from hpotter.env import logger, Session
from hpotter.docker.shell import fake_shell, get_string

# https://docs.python.org/3/library/socketserver.html
class TelnetHandler(socketserver.BaseRequestHandler):

    def creds(self, prompt):
        tries = 0
        response = ''
        while response == '':
            self.request.sendall(prompt)

            response = get_string(self.request, limit=256, telnet=True)

            tries += 1
            if tries > 2:
                raise IOError('no response')

        return response

    def handle(self):
        self.request.settimeout(30)

        self.session = Session()
        connection = tables.Connections(
            sourceIP=self.client_address[0],
            sourcePort=self.client_address[1],
            destIP=self.server.socket.getsockname()[0],
            destPort=self.server.socket.getsockname()[1],
            proto=tables.TCP)
        self.session.add(connection)
        self.session.commit()

        logger.debug('Before creds')
        try:
            username = self.creds(b'Username: ')
            password = self.creds(b'Password: ')
        except:
            logger.debug('Except creds')
            Session.remove()
            self.request.close()
            return
        logger.debug('After creds')

        creds = tables.Credentials(username=username, password=password, \
            connection=connection)
        self.session.add(creds)
        self.session.commit()

        self.request.sendall(b'Last login: Mon Nov 20 12:41:05 2017 from 8.8.8.8\n')

        prompt = b'\n$: ' if username in ('root', 'admin') else b'\n#: '
        try:
            fake_shell(self.request, self.session, connection, prompt, \
                telnet=True)
        except:
            pass

        Session.remove()
        self.request.close()

class TelnetServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

def start_server():
    hpotter.env.telnet_server = TelnetServer(('0.0.0.0', 23), TelnetHandler)
    threading.Thread(target=hpotter.env.telnet_server.serve_forever).start()

def stop_server():
    if hpotter.env.telnet_server:
        hpotter.env.telnet_server.shutdown()
