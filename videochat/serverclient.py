import socket, videosocket
from videofeed1 import VideoFeed
from threading import Thread,Timer
import Tkinter as tk
import tkMessageBox
import StringIO
import cv2

haveConnection = False
U_client_socket = U_address = None

class Daemon:
    def __init__(self):
        self.daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon_socket.bind(("", 6000))
        self.daemon_socket.listen(5)
        print "TCPServer Waiting for client on port 6000"

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
        global haveConnection, U_client_socket, U_address
        client_socket, address = U_client_socket, U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        videofeed = VideoFeed(1,"Server",1)
        tkMessageBox.showerror("Info", "Press \'q\' to quit!")
        try:
            while (True):
                key=cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                frame = vsock.vreceive()
                videofeed.set_frame(frame)
                frame = videofeed.get_frame()
                if (frame == None):
                    break
                vsock.vsend(frame)
        except:
            pass
        win.deiconify()
        del videofeed

class Client:
    def connect(self, ip_addr = "127.0.0.1"):
        global win
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip_addr, 6000))
        except:
            return ('Unavailable') # if Client can't get a connection to that IP
        win.withdraw() # Hide the Connect To window
        tkMessageBox.showerror("Info", "Press \'q\' to quit!")
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        videofeed = VideoFeed(1,"Client",1)
        try:
            while (True):
                key=cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                frame = videofeed.get_frame()
                vsock.vsend(frame)
                frame = vsock.vreceive()
                if (frame == None):
                    break
                videofeed.set_frame(frame)
        except:
            pass
        win.deiconify()
        del videofeed

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
entry_ip.pack(); button_connect.pack();
root.withdraw()

root.after(0, constantlyCheck)
root.mainloop()