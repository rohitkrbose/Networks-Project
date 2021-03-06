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
        global haveConnection, U_client_socket, U_address
        client_socket, address = U_client_socket, U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        videofeed = VideoFeed(1,"Server",1)
        tkMessageBox.showerror("Info", "Press \'q\' to quit!")
        try:
            while (True):
                key=cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    win.deiconify()
                    break
                frame = vsock.vreceive()
                videofeed.set_frame(frame)
                frame = videofeed.get_frame()
                vsock.vsend(frame)
        except:
            print ('Exception occurred')
        cv2.destroyAllWindows()

class Client:
    def connect(self, name, ip_addr = "127.0.0.1"):

        global win
        dummmySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            dummySocket.connect((ip_addr, 6001))
        except:
            return ('Unavailable') # if Client can't get a connection to that IP
        
        # Call function to obtain IP from dummy server
        targetIP = sendConnReq(dummySocket, myName='CLIENTA' ,target=name)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((targetIP[0], int(targetIP[1])))
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
                    win.deiconify()
                    break
                frame = videofeed.get_frame()
                vsock.vsend(frame)
                frame = vsock.vreceive()
                videofeed.set_frame(frame)
        except:
            print ('Expcetion occurred')
        cv2.destroyAllWindows()

def constantlyCheck(): # I am the server! This is a helper function for the daemon.
    global haveConnection, server, win
    # Here we should have an option: To reject or to accept. Only accept code is written here.
    if (haveConnection == True): # If daemon listened to some shit
        win.withdraw()  # Hide the Connect To window
        haveConnection = False
        server.connect() # Initiate video chat as server
    root.after(2, constantlyCheck) # Run this function again after 2 seconds


def sendConnServer(myName, serverIP):
    '''
        Requests the server to start serving it
    '''
    dummmySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        dummySocket.connect((ip_addr, 6001))


def sendConnReq(sock, myName, target):
    '''
        Takes my server connection socket, myName and target name
    '''
    toSend = "CONNECT," + target
    sock.send(bytes(toSend, 'utf-8'))
    msg = sock.rcv().decode('utf-8')

    if msg == "NOT AVAILABLE":
        return None
    elif msg == "BUSY":
        return None
    else:
        return msg.split(',')


def connectTo(): # I am the client!
    global win, ip, client
    name = tName.get()
    result = client.connect(name) # Initiate video chat as client
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

tName = tk.Entry(win) # targetName
button_connect = tk.Button(win, text = 'Connect To', command = lambda: connectTo()) # Connect to IP

tName.pack();
button_connect.pack();

root.withdraw()

root.after(0, constantlyCheck)
root.mainloop()
