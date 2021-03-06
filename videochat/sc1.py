import socket, videosocket
from videofeed import VideoFeed
from threading import Thread,Timer
from PIL import ImageTk
import Tkinter as tk
import tkMessageBox
import StringIO

haveConnection = False
videoRunning = True
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
            if (haveConnection == True): # if it is already engaged with someone, ignore the new request
                continue
            haveConnection = True # if it is not engaged, set this flag variable to true
            U_client_socket = cs; U_address = addr; # store client_socket and client address in global variables, as this is a thread
            print "I got a connection from ", addr

class Server:
    def connect(self):
        global haveConnection, U_client_socket, U_address, videoRunning, quit_win, root
        client_socket, address = U_client_socket, U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        # quit_win.deiconify()
        videofeed = VideoFeed(1,"Server",1)
        try:
            while (videoRunning):
                frame = vsock.vreceive()
                print("Frame received")
                root.set_frame(frame)
                frame = videofeed.get_frame()
                print("Obtained frame")
                vsock.vsend(frame)
                print("Send frame")
        except AttributeError as e:
            print("Some Exception")

class Client:
    def connect(self, ip_addr = "127.0.0.1"):
        global win, videoRunning, quit_win, root
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip_addr, 6000))
        except:
            return ('Unavailable') # if Client can't get a connection to that IP
        # win.withdraw() # Hide the Connect To window
        # quit_win.deiconify()
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        videofeed = VideoFeed(1,"Client",1)
        try:
            while (videoRunning):
                frame = videofeed.get_frame()
                vsock.vsend(frame)
                frame = vsock.vreceive()
                # videofeed.set_frame(frame)
                root.set_frame(frame)
        except AttributeError as e:
            print("Some Exception")

def constantlyCheck (): # I am the server! This is a helper function for the daemon.
    global haveConnection, server, win
    # Here we should have an option: To reject or to accept. Only accept code is written here.
    if (haveConnection == True): # If daemon listened to some shit
        # win.withdraw()  # Hide the Connect To window
        haveConnection = False
        server.connect() # Initiate video chat as server
    root.root.after(2, constantlyCheck) # Run this function again after 2 seconds

def connectTo(): # I am the client!
    global win, ip, client, root
    ip = root.entry_ip.get()
    result = client.connect(ip) # Initiate video chat as client
    if (result != None):
        tkMessageBox.showerror("Error", "Nobody there!")

def changeVideoState ():
    global videoRunning
    videoRunning = False

daemon = Daemon()
server = Server()
client = Client()

thread_daemon = Thread(target = daemon.start)
thread_daemon.start()

ip = ''

# Tkinter stuff

class Master:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Client")
        self.entry_ip = tk.Entry(self.root) # IP entry
        self.button_connect = tk.Button(self.root, text = 'Connect To', command = lambda: connectTo()) # Connect to IP
        self.button_quit = tk.Button(self.root, text = 'Quit', command = lambda: changeVideoState()) # Alter video state variable
        # self.panel = tk.Label()
        self.panel = None
        
        self.entry_ip.pack(); 
        self.button_connect.pack();
        self.button_quit.pack()

    def set_frame(self,frame):
        frame = ImageTk.PhotoImage(frame)
        if self.panel == None:
            self.panel = tk.Label(image=frame)
            self.panel.image = frame
            self.panel.pack()
        else:
            self.panel.configure(image=frame)
            self.panel.image = frame


root = Master()
root.root.after(0, constantlyCheck)
root.root.mainloop()
