import Tkinter as tk
import tkMessageBox
import auth # Imports auth
import sys # Imports sys, used to end the program later

# This file is for the client

class Daemon:
    def __init__(self, dsock, masterObj):
        self.daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon_socket.bind(("", 6001))
        self.daemon_socket.listen(5)
        print "TCPServer Waiting for Client on port 6001"
        thread_daemon = Thread(target = self.start)
        thread_daemon.start()

        self.masterObj = masterObj
        self.dsock = dsock

    def start(self):
        while True:
            cs, addr = self.daemon_socket.accept()
            if (self.masterObj.haveConnection == True): # if it is already engaged with someone, ignore the new request
                continue
            
            self.masterObj.haveConnection = True # if it is not engaged, set this flag variable to true
            self.masterObj.U_client_socket = cs; 
            self.masterObj.U_address = addr; # store client_socket and client address in global variables, as this is a thread
            print "I got a connection from ", addr

class Server:
    def __init__(self, dsock, masterObj):
        self.dummySock = dsock
        self.masterObj = masterObj

    def connect(self):
        global haveConnection, U_client_socket, U_address
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
    def __init__(self, dsock, masterObj):
        self.dummySock = dsock
        self.masterObj = masterObj

    def connect(self, ip_addr = "127.0.0.1"):
        global win
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

class Master:
    def __init__(self):

        # Tk Stuff
        self.root = tk.Tk() # Declares root as the tkinter main window
        self.root.title("Chat Client")

        self.haveConnection = False
        self.videoRunning = True
        self.U_client_socket = None
        self.U_address = None

        self.client = None
        self.server = None

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

        # self.label = tk.Label(self.root, text = 'This is your main window and you can input anything you want here')
        # self.label.pack()

        # Hide useless windows at first
        self.root.withdraw()
        self.win_auth2.withdraw()

    def postLogin(self):
        '''
            This is called after authenticate_otp
        '''
        self.vidWindow = tk.Toplevel();
        self.entry_ip = tk.Entry(self.vidWindow) # IP entry
        self.button_connect = tk.Button(self.vidWindow, text = 'Connect To', command = lambda: self.connectTo()) # Connect to IP

        self.entry_ip.pack()
        self.button_connect.pack()
        self.vidWindow.deiconify()

    def authenticate_email(self):
        email = self.entry_email.get()
        pw = self.entry_pw.get()
        if (auth.verify_mail(email,pw) == True): # Checks whether username and password are correct
            self.win_auth1.destroy() # Removes email window
            self.win_auth2.deiconify() # Unhides OTP window
            self.otp = auth.send_OTP(email)
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
            self.server.connect() # Initiate video chat as server
        self.root.after(2, self.constantlyCheck) # Run this function again after 2 seconds

    def connectTo(self): # I am the client!
        ip = self.entry_ip.get()
        result = self.client.connect(ip) # Initiate video chat as client
        if (result != None):
            tkMessageBox.showerror("Error", "Nobody there!")


if __name__ == '__main__':
    masterObj = Master()
    masterObj.first_pages()
    root = masterObj.root
    
    sIp = sys.argv[1] # server IP
    sPort = sys.argv[2] # server Port
    dummmySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        dummySocket.connect((sIp,sPort))
    except:
        print "Server Port/IP unavailable/incorrect"

    daemon = Daemon(dummySocket, masterObj)
    masterObj.server = Server(dummySocket, masterObj)
    masterObj.client = Client(dummySocket, masterObj)

    root.mainloop() # Starts the event loop for the main window
