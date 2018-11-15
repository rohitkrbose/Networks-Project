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

# This file is for the client

class Daemon:
    def __init__(self):
        self.daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon_socket.bind(("", 6000))
        self.daemon_socket.listen(5)
        print "TCPServer Waiting for Client on port 6000"
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
        # global haveConnection, U_client_socket, U_address
        client_socket, address = master.U_client_socket, master.U_address # retrieve info from global variables (changes made by Daemon)
        vsock = videosocket.videosocket(client_socket) # establish a video connection
        master.connWindow.withdraw() # Hide the Connect To window
        try:
            master.vidWindow.deiconify()
            while (True):
                if (master.acceptFlag == 2):
                    frame = None
                else:
                    frame = vsock.vreceive()
                if (frame == None):
                    raise Exception
                image = ImageTk.PhotoImage(Image.fromarray(master.videofeed.set_frame(frame)))
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
            print (e)
            print ('Some issue!')
        master.onClose()

class Client:
    def connectToOtherClient(self, ip_addr = "127.0.0.1"):
        # global win, video_win, panel, root, videofeed
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # the other guy/gal
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
                image = ImageTk.PhotoImage(Image.fromarray(master.videofeed.set_frame(frame)))
                if master.vidPanel is None: # first frame
                    master.vidPanel = tk.Label(master.vidWindow,image=image)
                    master.vidPanel.image = image
                    master.vidPanel.pack(side="left", padx=10, pady=10); master.vidWindow.update()
                else:
                    master.vidPanel.configure(image=image)
                    master.vidPanel.image = image; 
                    master.vidWindow.update()
        except Exception as e:
            print (e)
            print ('Some issue!')
        master.onClose()

    def connectToDummy (self,msg=''): # Connect to
        msg = "CONNECT," + master.entry_username.get()
        print (msg)
        master.dummySocket.send(msg.encode('utf-8'))
        r_msg = master.dummySocket.recv(2048).decode('utf-8')
        print (r_msg)
        if not (r_msg == 'NOT AVAILABLE' or r_msg == 'BUSY'): # Connection successful
            self.connectToOtherClient(ip_addr=r_msg)
        

class Master:
    def __init__(self, sIP, sPort):
        self.dummyIP = sIP
        self.dummySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.dummySocket.connect((self.dummyIP,sPort))
            pass
        except:
            print "Server Port/IP unavailable/incorrect"
        
        # Tk Stuff
        self.root = tk.Tk() # Declares root as the tkinter main window
        self.root.title("Chat Client")
        self.haveConnection = False
        self.acceptFlag = 0
        self.videoRunning = True
        self.U_client_socket = None
        self.U_address = None
        self.vidPanel = None
        self.callWindow = None

        self.videofeed = VideoFeed (1, "ZAMZAM", 1)

    def onClose (self):
        self.videofeed.cam.release()
        self.connWindow.deiconify()
        del self.videofeed
        self.videofeed = VideoFeed (1, "ZAMZAM", 1)
        self.vidWindow.destroy()
        self.vidWindow = tk.Toplevel()
        self.vidWindow.withdraw()
        msg = "CONNECTME," + self.email
        self.dummySocket.send(msg.encode('utf-8'))
        self.dummySocket.recv(2048).decode('utf-8')
        self.vidPanel = None
        self.acceptFlag = 0


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

    def postLogin(self):
        '''
            This is called after authenticate_otp
        '''
        self.connWindow = tk.Toplevel();
        self.vidWindow = tk.Toplevel();
        self.callWindow = tk.Toplevel();
        self.callLabel = tk.Label(self.callWindow,text='Incoming call!')
        self.entry_username = tk.Entry(self.connWindow) # IP entry
        self.button_endEverything = tk.Button(self.connWindow, text = 'Quit', command = lambda: self.endEverything())
        self.button_connect = tk.Button(self.connWindow, text = 'Connect To', command = lambda: self.connectTo()) # Connect to IP
        self.button_acceptCall = tk.Button(self.callWindow, text = "Accept", command = lambda: self.dealCall(True))
        self.button_rejectCall = tk.Button(self.callWindow, text = "Reject", command = lambda: self.dealCall(False))

        self.entry_username.pack()
        self.button_connect.pack()
        self.button_acceptCall.pack(); self.button_rejectCall.pack();
        self.button_endEverything.pack();
        self.vidWindow.withdraw()  # hide window
        self.callWindow.withdraw() # hide window

        # Send CONNECTME to dummyserver
        msg = "CONNECTME," + self.email
        self.dummySocket.send(msg.encode('utf-8'))
        print(self.dummySocket.recv(2048).decode('utf-8'))

    def dealCall (flag):
        if (flag == True):
            msg = "ACCEPT"
            self.acceptFlag = 1
        else:
            msg = "REJECT"
            self.acceptFlag = 2
        self.callWindow.withdraw()
        self.dummySocket.send(msg.encode('utf-8'))

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
            self.postLogin()
        else:
            tkMessageBox.showerror("Error", "Invalid OTP!")

    def quit(self):
        self.root.destroy() # Removes the top level window

    def constantlyCheck(self): # I am the server! This is a helper function for the daemon.
        # Here we should have an option: To reject or to accept. Only accept code is written here.
        if (self.haveConnection == True): # If daemon listened to some shit
            self.callWindow.deiconify()
            self.connWindow.withdraw()
            while (not self.acceptFlag):
                self.acceptFlag = self.acceptFlag
            self.haveConnection = False
            server.connect() # Initiate video chat as server
        self.root.after(2, self.constantlyCheck) # Run this function again after 2 seconds

    def connectTo(self): # I am the client!
        ip = self.entry_username.get()
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
