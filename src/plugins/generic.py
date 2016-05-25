import socket
import socketserver

# pass in socket, DB connection, logger

def get_address(): return ('127.0.0.1', 2000)

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())

# help from
# http://cheesehead-techblog.blogspot.com/2013/12/python-socketserver-and-upstart-socket.html
class MyServer(socketserver.TCPServer):
    def __init__(self, mysocket):
        self.mysocket = mysocket
        socketserver.TCPServer.__init__(self, None, MyTCPHandler)

    def server_bind(self):
        print('in server_bind')
        self.socket = self.mysocket


if __name__ == "__main__":
    mysocket = socket.socket()
    mysocket.bind(get_address())
    server = MyServer(mysocket)
    server.serve_forever()
