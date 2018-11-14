import socket, videosocket
from videofeed import VideoFeed
from threading import Thread,Timer
import Tkinter as tk
import tkMessageBox

haveConnection = False
U_client_socket = U_address = None
end = False

def closeVideo ():
    global end
    end = True

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
            if (haveConnection == True): # if it is already engaged with someone, ignore the new request
                continue
            haveConnection = True # if it is not engaged, set this flag variable to true
            U_client_socket = cs; U_address = addr; # store client_socket and client address in global variables, as this is a thread
            print "I got a connection from ", addr

class Server:
    global haveConnection, U_client_socket, U_address, end, tk
    def __init__ (self):
        self.videofeed = None
    def show (self):
        frame = vsock.vreceive()
        self.videofeed.set_frame(frame)
        frame = self.videofeed.get_frame()
        vsock.vsend(frame)
        if (end == False):
            tk.after(1,self.show)
    def connect(self):
        client_socket, address = U_client_socket, U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video 
        self.videofeed = VideoFeed(1,"A1",1)
        self.show()

class Client:
    global win, end, tk
    def __init__ (self):
        self.videofeed = None
    def show (self):
        frame = videofeed.get_frame()
        vsock.vsend(frame)
        frame = vsock.vreceive()
        videofeed.set_frame(frame)
        if (end == False):
            tk.after(1,self.show)
    def connect(self, ip_addr = "127.0.0.1"):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip_addr, 6000))
        except:
            return ('Unavailable') # if Client can't get a connection to that IP
        win.withdraw() # Hide the Connect To window
        vsock = videosocket.videosocket (client_socket) # establish a video connection
        self.videofeed = VideoFeed(1,"A2",1)

def constantlyCheck (): # I am the server! This is a helper function for the daemon.
    global haveConnection, server, win
    # Here we should have an option: To reject or to accept. Only accept code is written here.
    if (haveConnection == True): # If daemon listened to some shit
        win.withdraw()  # Hide the Connect To window
        haveConnection = False
        server.connect() # Initiate video chat as server
    root.after(2, constantlyCheck) # Run this function again after 2 seconds

def connectTo(): # I am the client!
    global win, ip, client
    ip = entry_ip.get()
    result = client.connect(ip) # Initiate video chat as client
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
button_connect = tk.Button(win, text = 'Connect To', command = lambda: connectTo()) # Connect to IP
button_exit = tk.Button(root, text = 'Quit', command = lambda: closeVideo())
entry_ip.pack(); button_connect.pack();
button_exit.pack()

root.after(0, constantlyCheck)
root.mainloop()