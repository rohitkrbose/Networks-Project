import socket, videosocket
from videofeed import VideoFeed
import threading
import time
import StringIO

occupied = False
zoom = False
videofeed = VideoFeed(1,"axax",1)
U_client_socket = ''
U_address = ''

class Daemon:
    def __init__(self):
        self.daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon_socket.bind(("", 6001))
        self.daemon_socket.listen(5)
        print "TCPServer Waiting for client on port 6000"

    def start(self):
        while True:
            cs, addr = self.daemon_socket.accept()
            if (occupied == True):
            	continue
            zoom = True
            U_client_socket = cs; U_address = addr;
            print "I got a connection from ", addr
            break

class Server:
    def start(self):
        client_socket, address = U_client_socket, U_address
        vsock = videosocket.videosocket(client_socket)
        while True:
            frame = vsock.vreceive()
            videofeed.set_frame(frame)
            frame = videofeed.get_frame()
            vsock.vsend(frame)

class Client:
    def __init__(self, ip_addr = "127.0.0.1"):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip_addr, 6000))
        self.vsock = videosocket.videosocket (self.client_socket)
        self.data = StringIO.StringIO()

    def connect(self):
        while True:
            print ('asdasd')
            frame=videofeed.get_frame()
            self.vsock.vsend(frame)
            frame = self.vsock.vreceive()
            videofeed.set_frame(frame)


if __name__ == "__main__":
    daemon = Daemon()
    thread_daemon = threading.Thread(target=daemon.start)
    thread_daemon.start()
    server = Server()
    while (True):
        if (zoom == True):
            server.start()
            break
    	time.sleep(5)
    	ip_addr = raw_input('Which IP do you want to connect to?\n')
    	if (ip_addr != 'N'):
            client = Client(ip_addr)
            client.connect()