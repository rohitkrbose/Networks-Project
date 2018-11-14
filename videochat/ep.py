from multiprocessing import Process,Queue,Pipe
import socket, videosocket
from videofeed import VideoFeed
from threading import Thread,Timer
import Tkinter as tk
import tkMessageBox
import pickle
from multiprocessing.reduction import ForkingPickler
import StringIO
from video_helper import V

haveConnection = False
U_client_socket = U_address = None
sock = None

def forking_dumps(obj):
    buf = StringIO.StringIO()
    ForkingPickler(buf).dump(obj)
    return buf.getvalue()

def spawnVideo_s ():
	global sock
	parent_conn,child_conn = Pipe()
	parent_conn.send(forking_dumps(sock))
	p = Process(target=V_s, args=(child_conn,))
	p.start()

def spawnVideo_c ():
	global sock
	parent_conn,child_conn = Pipe()
	parent_conn.send(forking_dumps(sock))
	p = Process(target=V_c, args=(child_conn,))
	p.start()

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
        global haveConnection, U_client_socket, U_address, sock
        client_socket, address = U_client_socket, U_address # retrieve info from global variables (changes made by Daemon)
        sock = client_socket
        spawnVideo_s()

class Client:
    def connect(self, ip_addr = "127.0.0.1"):
        global win, sock
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip_addr, 6000))
        except:
            return ('Unavailable') # if Client can't get a connection to that IP
        win.withdraw() # Hide the Connect To window
        sock = client_socket
        spawnVideo_c()

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