from tkinter import ttk, Tk, Toplevel

root = Tk()
welcome_window = Toplevel(root)
welcome_window.title('Welcome')

lab_window = Toplevel(root)
lab_window.title('Lab')

root.withdraw() # hide root window
lab_window.withdraw() # hide lab window

def goto_lab():
    welcome_window.destroy()
    lab_window.deiconify() # show lab window

button1 = ttk.Button(welcome_window, text='Close1',command=goto_lab)
button1.pack(padx=100, pady=50)

button2 = ttk.Button(lab_window, text='Close',command=quit)
button2.pack(padx=100, pady=50)

root.mainloop()