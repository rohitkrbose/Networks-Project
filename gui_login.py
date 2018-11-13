import tkinter as tk
from tkinter import messagebox
import auth # Imports auth
import sys # Imports sys, used to end the program later

def authenticate_email():
	global window_auth1, otp
	email = entry_email.get()
	pw = entry_pw.get()
	if (auth.verify_mail(email,pw) == True): # Checks whether username and password are correct
		win_auth1.destroy() # Removes email window
		win_auth2.deiconify() # Unhides OTP window
		otp = auth.send_OTP(email)
	else:
		messagebox.showerror("Error", "Invalid credentials!")

def authenticate_otp():
	global window_auth2
	entered_otp = entry_otp.get()
	if (otp == entered_otp):
		win_auth2.destroy() # Removes OTP window
		root.deiconify() # Unhides root window
	else:
		messagebox.showerror("Error", "Invalid OTP!")

def quit():
    win_auth1.destroy() # Removes the top level window
    root.destroy() # Removes the hidden root window
    sys.exit() # Ends the script

# Tk Stuff
root = tk.Tk() # Declares root as the tkinter main window
root.title("Chat Client")
win_auth1 = tk.Toplevel()
win_auth2 = tk.Toplevel()

# Variables used everywhere
email = ''
pw = ''
otp = ''

# Entries

entry_email = tk.Entry(win_auth1) # Email entry
entry_pw = tk.Entry(win_auth1, show = '*') # Password entry
entry_otp = tk.Entry(win_auth2) # OTP entry

# Buttons
button_login = tk.Button(win_auth1, text = 'Login', command = lambda: authenticate_email()) # Login button
button_quit = tk.Button(win_auth1, text = 'Quit', command = lambda: quit()) # Exit button
button_verifyOTP = tk.Button(win_auth2, text = 'Verify OTP', command = lambda: authenticate_otp()) # See if user has correct OTP

# Pack
entry_email.pack(); entry_pw.pack(); button_login.pack(); button_quit.pack()
entry_otp.pack(); button_verifyOTP.pack();

label = tk.Label(root, text = 'This is your main window and you can input anything you want here')
label.pack()

# Hide useless windows at first
root.withdraw()
win_auth2.withdraw()

root.mainloop() # Starts the event loop for the main window