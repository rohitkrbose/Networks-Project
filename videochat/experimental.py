import socket, videosocket
from videofeed import VideoFeed
from threading import Thread,Timer
import Tkinter as tk
import tkMessageBox

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
            if (haveConnection == True):
                continue
            haveConnection = True
            U_client_socket = cs; U_address = addr;
            print "I got a connection from ", addr

class Server:
    def connect(self):
        global haveConnection, U_client_socket, U_address
        client_socket, address = U_client_socket, U_address
        vsock = videosocket.videosocket(client_socket)
        videofeed = VideoFeed(1,"A1",1)
        while True:
            frame = vsock.vreceive()
            videofeed.set_frame(frame)
            frame = videofeed.get_frame()
            vsock.vsend(frame)

class Client:
    def connect(self, ip_addr = "127.0.0.1"):
        global win
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip_addr, 6000))
        except:
            return ('Unavailable')
        win.withdraw()
        vsock = videosocket.videosocket (client_socket)
        videofeed = VideoFeed(1,"A2",1)
        while True:
            frame = videofeed.get_frame()
            vsock.vsend(frame)
            frame = vsock.vreceive()
            videofeed.set_frame(frame)

def constantlyCheck (): # I am the server!
    global haveConnection, server, win
    if (haveConnection == True):
        win.withdraw()
        haveConnection = False
        server.connect()
    root.after(3, constantlyCheck)

def connectTo(): # I am the client!
    global win, ip, client
    ip = entry_ip.get()
    result = client.connect(ip)
    if (result != None):
        tkMessageBox.showerror("Error", "Nobody there!")

daemon = Daemon()
server = Server()
client = Client()

thread_daemon = Thread(target = daemon.start)
thread_daemon.start()

# Tkinter stuff
root = tk.Tk()
root.title("Chat Client")
win = tk.Toplevel()
ip = ''
entry_ip = tk.Entry(win) # IP entry
button_connect = tk.Button(win, text = 'Connect', command = lambda: connectTo()) # Connect to IP
entry_ip.pack(); button_connect.pack();
root.withdraw()

root.after(0, constantlyCheck)
root.mainloop()