import Tkinter as tk
import tkMessageBox
import auth # Imports auth
import sys # Imports sys, used to end the program later

class Master:
    def __init__(self):

        # Tk Stuff
        self.root = tk.Tk() # Declares root as the tkinter main window
        self.root.title("Chat Client")

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
        self.entry_ip = tk.Entry(self.root) # IP entry
        self.button_connect = tk.Button(self.root, text = 'Connect To', command = lambda: connectTo()) # Connect to IP

        self.entry_ip.pack()
        self.button_connect.pack()

        # Hide useless windows at first
        self.root.withdraw()
        self.win_auth2.withdraw()

    def postLogin(self):
        pass

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
            self.root.deiconify() # Unhides root window
        else:
            tkMessageBox.showerror("Error", "Invalid OTP!")

    def quit(self):
        self.win_auth1.destroy() # Removes the top level window
        self.root.destroy() # Removes the hidden root window
        sys.exit() # Ends the script

masterObj = Master()
masterObj.first_pages()
root = masterObj.root
root.mainloop() # Starts the event loop for the main window
