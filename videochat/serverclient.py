import socket, videosocket
from videofeed import VideoFeed
import threading
import time
import StringIO

occupied = False
zoom = False
videofeed = VideoFeed(1,"axax",1)

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", 6000))
        self.server_socket.listen(5)
        # self.videofeed = VideoFeed(1,"server",1)
        print "TCPServer Waiting for client on port 6000"

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            if (occupied == True):
            	continue
            zoom = True
            print "I got a connection from ", address
            vsock = videosocket.videosocket(client_socket)
            while True:
                print ('asdasd')
                frame = vsock.vreceive()
                videofeed.set_frame(frame)
                frame = videofeed.get_frame()
                vsock.vsend(frame)

class Client:
    def __init__(self, ip_addr = "127.0.0.1"):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip_addr, 6001))
        self.vsock = videosocket.videosocket (self.client_socket)
        # self.videofeed = VideoFeed(1,"client",1)
        self.data = StringIO.StringIO()

    def connect(self):
        while True:
            frame=videofeed.get_frame()
            self.vsock.vsend(frame)
            frame = self.vsock.vreceive()
            videofeed.set_frame(frame)

if __name__ == "__main__":
    server = Server()
    thread_server = threading.Thread(target=server.start)
    while (True):
    	time.sleep(5)
    	ip_addr = raw_input('Which IP do you want to connect to?\n')
    	if (ip_addr != 'N'):
            thread_server.stop()
            client = Client(ip_addr)
            client.connect()
