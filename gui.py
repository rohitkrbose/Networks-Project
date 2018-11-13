from tkinter import *

class mainWindow:

    def __init__(self, master):
        self.master = master
        self.master.title("Bose-Mittal-Sharma Video Client")

        btn = Button(self.master, text="Click Here", command=self.btnAction)
        btn.pack()
        # btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        closeBtn = Button(self.master, text="Close", command=self.master.quit)
        closeBtn.pack()

    def btnAction(self):
        print("Called button action command")



root = Tk()
gui =  mainWindow(root)
root.mainloop()
