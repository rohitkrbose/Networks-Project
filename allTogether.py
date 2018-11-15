import Tkinter as tk
import tkMessageBox
import auth # Imports auth
import sys # Imports sys, used to end the program later
import socket, videosocket
from threading import Thread
from videofeed1 import VideoFeed
import socket, videosocket
from videofeed1 import VideoFeed
from threading import Thread,Timer
from PIL import Image
from PIL import ImageTk
import Tkinter as tk
import tkMessageBox
import StringIO
import cv2
from cvFilters.filters import get_Frame
# This file is for the client

class Daemon:
    def __init__(self):
        self.daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon_socket.bind(("", 6000))
        self.daemon_socket.listen(5)
        print "Waiting for Chat"
        thread_daemon = Thread(target = self.start)
        thread_daemon.start()

    def start(self):
        while True:
            cs, addr = self.daemon_socket.accept()
            if (master.haveConnection == True): # if it is already engaged with someone, ignore the new request
                continue
            master.haveConnection = True # if it is not engaged, set this flag variable to true
            master.U_client_socket = cs; 
            master.U_address = addr; # store client_socket and client address in global variables, as this is a thread
            print "I got a connection from ", addr

class Server:
    def connect(self):
        tkMessageBox.showinfo("Info", "Connection accepted!")
        # global haveConnection, U_client_socket, U_address
        client_socket, address = master.U_client_socket, master.U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        master.connWindow.withdraw() # Hide the Connect To window
        try:
            master.vidWindow.deiconify()
            while (True):
                frame = vsock.vreceive()
                if (frame == None):
                    raise Exception

                frame = master.videofeed.set_frame(frame)
                # Specify choice for Filter here
                if master.videoMode != 0:
                    frame = get_Frame(frame, master.videoMode)
                image = ImageTk.PhotoImage(Image.fromarray(frame))

                if master.vidPanel is None:
                    master.vidPanel = tk.Label(master.vidWindow,image=image)
                    master.vidPanel.image = image
                    master.vidPanel.pack(side="left", padx=10, pady=10)
                    master.vidWindow.update()
                else:
                    master.vidPanel.configure(image=image)
                    master.vidPanel.image = image
                    master.vidWindow.update()
                frame = master.videofeed.get_frame()
                vsock.vsend(frame)
        except Exception as e:
            pass
            # print (e)
            # print ('Some issue!')
        master.onClose()
        master.connWindow.deiconify()
        self.connectExitTrigger()

    def connectExitTrigger (self, msg=''): # Connect to
        msg = "CONNECTME," + master.email
        master.dummySocket.send(msg.encode('utf-8'))
        r_msg = master.dummySocket.recv(2048).decode('utf-8')

class Client:
    def connectToOtherClient(self, ip_addr = "127.0.0.1"):
        # global win, video_win, panel, root, videofeed
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # the other guy/gal
        print (ip_addr, 'asdsd')
        client_socket.connect((ip_addr, 6000))  
        master.connWindow.withdraw() # Hide the Connect To window
        tkMessageBox.showinfo("Info", "Connection successful!")
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        try:
            master.vidWindow.deiconify()
            while (True):
                frame = master.videofeed.get_frame()
                vsock.vsend(frame)
                frame = vsock.vreceive()
                if (frame == None):
                    raise Exception # Timeout

                frame = master.videofeed.set_frame(frame)
                # Specify choice for Filter here
                if master.videoMode != 0:
                    frame = get_Frame(frame, master.videoMode)

                image = ImageTk.PhotoImage(Image.fromarray(frame))

                if master.vidPanel is None: # first frame
                    master.vidPanel = tk.Label(master.vidWindow,image=image)
                    master.vidPanel.image = image
                    master.vidPanel.pack(side="left", padx=10, pady=10); master.vidWindow.update()
                else:
                    master.vidPanel.configure(image=image)
                    master.vidPanel.image = image; 
                    master.vidWindow.update()
        except Exception as e:
            pass
            # print (e)
            # print ('Some issue!')
        master.onClose()
        master.connWindow.deiconify()

    def connectToDummy (self,msg=''): # Connect to
        msg = "CONNECT," + msg
        # print (msg)
        master.dummySocket.send(msg.encode('utf-8'))
        r_msg = master.dummySocket.recv(2048).decode('utf-8')
        # print (r_msg)
        if not (r_msg == 'NOT AVAILABLE' or r_msg == 'BUSY'): # Connection successful
            self.connectToOtherClient(ip_addr=r_msg)
            msg = "CONNECTME," + master.email
            master.dummySocket.send(msg.encode('utf-8'))
            r_msg = master.dummySocket.recv(2048).decode('utf-8')
        # elif (r_msg == 'NOT AVAILABLE'):
        #     tkMessageBox.showerror("Error", u + " is unavailable.")
        # else:
        #     tkMessageBox.showerror("Error", u + " is busy.")
        

class Master:
    def __init__(self, sIP, sPort):
        self.videoMode = 0
        self.videofeed = VideoFeed (1, "ZAMZAM", 1)
        self.vidPanel = None
        self.dummyIP = sIP
        self.dummySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.dummySocket.connect((self.dummyIP,sPort))
            pass
        except:
            tkMessageBox.showerror("Error", "Server Port/IP unavailable/incorrect")
            self.root.destroy()

        # Tk Stuff
        self.root = tk.Tk() # Declares root as the tkinter main window
        self.root.title("Chat Client")
        self.haveConnection = False
        self.videoRunning = True
        self.U_client_socket = None
        self.U_address = None
        self.var = tk.IntVar()

    def onClose (self):
        self.videofeed.cam.release()
        del self.videofeed
        self.videofeed = VideoFeed (1, "ZAMZAM", 1)
        self.vidWindow.destroy()
        self.vidWindow = tk.Toplevel()
        self.vidWindow.withdraw()
        self.vidPanel = None


    def first_pages(self):
        # Variables used everywhere
        self.email = ''
        self.pw = ''
        self.otp = ''

        self.win_auth1 = tk.Toplevel()
        self.win_auth2 = tk.Toplevel()

        # Entries
        self.entry_email = tk.Entry(self.win_auth1) # Email entry
        self.entry_pw = tk.Entry(self.win_auth1, show = '*') # Password entry
        self.entry_otp = tk.Entry(self.win_auth2) # OTP entry

        # Buttons
        self.button_login = tk.Button(self.win_auth1, text = 'Login', command = lambda: self.authenticate_email()) # Login button
        self.button_quit = tk.Button(self.win_auth1, text = 'Quit', command = lambda: self.quit()) # Exit button
        self.button_verifyOTP = tk.Button(self.win_auth2, text = 'Verify OTP', command = lambda: self.authenticate_otp()) # See if user has correct OTP

        # Pack
        self.entry_email.pack(); self.entry_pw.pack(); self.button_login.pack(); self.button_quit.pack()
        self.entry_otp.pack(); self.button_verifyOTP.pack();

        # Hide useless windows at first
        self.root.withdraw()
        self.win_auth2.withdraw()

    def sel(self):
        self.videoMode = self.var.get()
        # print (self.videoMode)

    def postLogin(self):
        '''
            This is called after authenticate_otp
        '''
        self.connWindow = tk.Toplevel();
        self.vidWindow = tk.Toplevel();
        self.entry_username = tk.Entry(self.connWindow) # IP entry
        self.button_connect = tk.Button(self.connWindow, text = 'Connect To', command = lambda: self.connectTo()) # Connect to IP
        self.button_endEverything = tk.Button(self.connWindow, text = 'Quit', command = lambda: self.endEverything())
        self.marquee = tk.Label(self.connWindow, text = '---Mode---')
        self.entry_username.pack()
        self.button_connect.pack()
        self.marquee.pack()
        self.vidWindow.deiconify()

        # Send CONNECTME to dummyserver
        msg = "CONNECTME," + self.email
        self.dummySocket.send(msg.encode('utf-8'))
        r_msg = self.dummySocket.recv(2048).decode('utf-8')

        # CONNECT SHIT
        R1 = tk.Radiobutton(self.connWindow, text="None", variable=self.var, value=0, command=self.sel)
        R1.pack()
        R2 = tk.Radiobutton(self.connWindow, text= "Hat", variable=self.var, value=1, command=self.sel)
        R2.pack()
        R3 = tk.Radiobutton(self.connWindow, text="Moustache", variable=self.var, value=2, command=self.sel)
        R3.pack()
        R4 = tk.Radiobutton(self.connWindow, text="Ha-stache", variable=self.var, value=3, command=self.sel)
        R4.pack()
        R5 = tk.Radiobutton(self.connWindow, text="Doggy Style", variable=self.var, value=4, command=self.sel)
        R5.pack()

        self.button_endEverything.pack();

    def authenticate_email(self):
        self.email = self.entry_email.get()
        pw = self.entry_pw.get()
        if (auth.verify_mail(self.email,pw) == True): # Checks whether username and password are correct
            self.win_auth1.destroy() # Removes email window
            self.win_auth2.deiconify() # Unhides OTP window
            self.otp = auth.send_OTP(self.email)
        else:
            tkMessageBox.showerror("Error", "Invalid credentials!")

    def authenticate_otp(self):
        entered_otp = self.entry_otp.get()
        if (self.otp == entered_otp):
            self.win_auth2.destroy() # Removes OTP window
            # self.root.deiconify() # Unhides root window
            self.postLogin()
        else:
            tkMessageBox.showerror("Error", "Invalid OTP!")

    def quit(self):
        self.win_auth1.destroy() # Removes the top level window
        # self.root.destroy() # Removes the hidden root window

    def constantlyCheck(self): # I am the server! This is a helper function for the daemon.

        # Here we should have an option: To reject or to accept. Only accept code is written here.
        if (self.haveConnection == True): # If daemon listened to some shit
            # win.withdraw()  # Hide the Connect To window
            self.haveConnection = False
            server.connect() # Initiate video chat as server
        self.root.after(2, self.constantlyCheck) # Run this function again after 2 seconds

    def connectTo(self): # I am the client!
        ip = self.entry_username.get()
        print (ip)
        self.videoMode = self.var.get()
        result = client.connectToDummy(ip) # Initiate video chat as client
        if (result != None):
            tkMessageBox.showerror("Error", "Nobody there!")

    def endEverything (self):
        msg = 'DISCONNECTME,' + self.email
        self.dummySocket.send(msg.encode('utf-8'))
        self.root.destroy()
        sys.exit(0)

master = Master(sys.argv[1],int(sys.argv[2])) # send server IP
master.first_pages()
root = master.root
daemon = Daemon()
server = Server()
client = Client()
root.after(0, master.constantlyCheck)
root.mainloop() # Starts the event loop for the main window
