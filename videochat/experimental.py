import socket, videosocket
from videofeed import VideoFeed
from threading import Thread
import time
import StringIO

occupied = False
haveConnection = False
U_client_socket = U_address = None

class Daemon:
    def __init__(self):
        self.daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon_socket.bind(("", 6001))
        self.daemon_socket.listen(5)
        print "TCPServer Waiting for client on port 6001"

    def start(self):
        global haveConnection, U_client_socket, U_address
        while True:
            cs, addr = self.daemon_socket.accept()
            if (occupied == True):
            	continue
            haveConnection = True
            U_client_socket = cs; U_address = addr;
            print "I got a connection from ", addr

class Server:
    def start(self):
        client_socket, address = U_client_socket, U_address
        vsock = videosocket.videosocket(client_socket)
        videofeed = VideoFeed(1," ",1)
        while True:
            frame = vsock.vreceive()
            videofeed.set_frame(frame)
            frame = videofeed.get_frame()
            vsock.vsend(frame)

class Client:
    def connect(self, ip_addr = "127.0.0.1"):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_addr, 6000))
        vsock = videosocket.videosocket (client_socket)
        videofeed = VideoFeed(1," ",1)
        while True:
            frame=videofeed.get_frame()
            self.vsock.vsend(frame)
            frame = self.vsock.vreceive()
            videofeed.set_frame(frame)


if __name__ == "__main__":
    daemon = Daemon()
    thread_daemon = Thread(target=daemon.start)
    thread_daemon.start()
    server = Server()
    client = Client()
    while (True):
        if (haveConnection == True): # daemon listened to some shit
            server.start()
    	ip_addr = raw_input('Which IP do you want to connect to?\n')
    	if (ip_addr != 'N'):
            client = Client()
            client.connect(ip_addr)