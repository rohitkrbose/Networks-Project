import socket, videosocket
from videofeed1 import VideoFeed
from threading import Thread,Timer
from PIL import Image
from PIL import ImageTk
import Tkinter as tk
import tkMessageBox
import StringIO
import cv2

haveConnection = False
U_client_socket = U_address = None
videofeed = VideoFeed(1,"ZAMZAM",1)

def onClose ():
    global root
    videofeed.cam.release()
    root.quit()

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
        global haveConnection, U_client_socket, U_address, root, video_win, panel, videofeed
        client_socket, address = U_client_socket, U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        tkMessageBox.showerror("Info", "Press \'q\' to quit!")
        try:
            while (True):
                frame = vsock.vreceive()
                image = ImageTk.PhotoImage(Image.fromarray(videofeed.set_frame(frame)))
                if panel is None:
                    panel = tk.Label(root,image=image)
                    panel.image = image
                    panel.pack(side="left", padx=10, pady=10)
                    root.update()
                else:
        			panel.configure(image=image)
        			panel.image = image; root.update()
                frame = videofeed.get_frame()
                if (frame == None):
                    break
                vsock.vsend(frame)
        except Exception as e:
        	print (e)
        	print ('Some issue!')
        win.deiconify()

class Client:
    def connect(self, ip_addr = "127.0.0.1"):
        global win, video_win, panel, root, videofeed
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip_addr, 6000))
        except:
            return ('Unavailable') # if Client can't get a connection to that IP
        win.withdraw() # Hide the Connect To window
        tkMessageBox.showerror("Info", "Press \'q\' to quit!")
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        try:
            while (True):
                frame = videofeed.get_frame()
                vsock.vsend(frame)
                frame = vsock.vreceive()
                if (frame == None):
                    break
                image = ImageTk.PhotoImage(Image.fromarray(videofeed.set_frame(frame)))
                if panel is None:
                	panel = tk.Label(root,image=image)
                	panel.image = image
                	panel.pack(side="left", padx=10, pady=10); root.update()
                else:
                	panel.configure(image=image)
                	panel.image = image; root.update()
        except:
            pass
        win.deiconify()

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
root.wm_protocol("WM_DELETE_WINDOW", onClose)
win = tk.Toplevel()
video_win = tk.Toplevel()
video_win.withdraw()
panel = None

ip = ''
entry_ip = tk.Entry(win) # IP entry
button_connect = tk.Button(win, text = 'Connect To', command = lambda: connectTo()) # Connect to IP
entry_ip.pack(); button_connect.pack();

root.after(0, constantlyCheck)
root.mainloop()
