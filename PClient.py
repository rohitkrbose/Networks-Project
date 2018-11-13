import socket
from threading import Thread
import tkinter as tk

import videosocket
from videofeed import VideoFeed
from config import *

class Client:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.settimeout(5)
        self.buffer_size = 2048
        self.vsock = videosocket.VideoSocket(self.socket)
        self.is_video_call = False
        self.videofeed = None

    def receive(self):
        while True:
            if self.is_video_call:
                if not self.videofeed:
                    self.videofeed = VideoFeed("client_cam", 1)
                frame = self.videofeed.get_frame()
                self.vsock.vsend(frame)
                rcvd_frame = self.vsock.vreceive()
                self.videofeed.set_frame(rcvd_frame)
            else:
                # free up webcam in case not in use
                if self.videofeed:
                    del self.videofeed

                msg = self.socket.recv(self.buffer_size)
                if msg == bytes("VIDEO_CALL_START", ENCODING):
                    self.is_video_call = True
                elif msg == bytes("VIDEO_CALL_REQUEST", ENCODING):
                    # someone wants to videochat with you
                    self.receive_vcall()
                else:
                    self.update_gui(msg, False)

    def send(self, msg=None):
        if msg is None:
            msg = msg_box.get()
            msg_box.delete(0, tk.END)
            self.socket.send(bytes(msg, ENCODING))
        else:
            self.socket.send(msg)

    def initiate_video_call(self):
        self.send(bytes("VIDEO_CALL_START", ENCODING))
        usernames = self.socket.recv(self.buffer_size).decode(ENCODING)
        names = usernames.split("$")[:-1]

        num_online = len(names)
        root = tk.Tk()
        root.geometry("300x%s" %(str((2 + num_online) * 100)))
        if num_online == 0:
            l = tk.Label(root, text="No users online, try again later!!", padx=20, pady=10)
            l.pack()
        else:
            l = tk.Label(root, text="Select the person whose face you want to see!!")
            l.pack()

        for n in names:
            b = tk.Button(root, text=n, command=lambda: self.decide_target(root, n))
            b.pack()

        qb = tk.Button(root, text="Quit", command=lambda: self.decide_target(root, None))
        qb.pack()
        root.mainloop()

    def decide_target(self, root, target):
        if target:
            self.send(bytes(target, ENCODING))
        else:
            self.send(bytes("VIDEO_CALL_ABORT", ENCODING))
        root.destroy()

    def update_gui(self, msg, is_sent=False):
        display_listbox.insert("end", msg.decode(ENCODING))

    def receive_vcall(self):
        # get username of who wants to talk with you
        from_uname = self.socket.recv(self.buffer_size).decode(ENCODING)
        root = tk.Tk()
        root.geometry("300x300")
        l = tk.Label(root, text="Your beloved %s wants to see your face !!" %(from_uname),
                padx=20, pady=20)
        l.pack()
        b1 = tk.Button(root, text="Accept", command=lambda: self.send_confirmation(root, from_uname, True))
        b1.pack()

        b2 = tk.Button(root, text="Reject", command=lambda: self.send_confirmation(root, from_uname, False))
        b2.pack()
        root.mainloop()

    def send_confirmation(self, root, accept_from, decision):
        if decision:
            msg = bytes("VIDEO_CALL_ACCEPT", ENCODING)
        else:
            msg = bytes("VIDEO_CALL_REJECTED", ENCODING)
        self.send(msg)
        self.send(bytes(accept_from, ENCODING))
        root.destroy()

client = Client()
white = "#fff"

msg_box = None
display_listbox = None

def cleanup(root):
    root.destroy()
    client.send(bytes("QUIT", ENCODING))


def design_top(root, master):
    fr1 = tk.Frame(master, bg=white, width=150, height=40, padx=10)
    fr1.pack(side=tk.LEFT)
    fr1.pack_propagate(0)

    btn1 = tk.Button(fr1, text="Video Call", height=40, command=client.initiate_video_call)
    btn1.pack(fill=tk.BOTH)

    fr2 = tk.Frame(master, bg=white, width=150, height=40, padx=10)
    fr2.pack(side=tk.LEFT)
    fr2.pack_propagate(0)

    btn2 = tk.Button(fr2, text="Quit", height=40, command=lambda: cleanup(root))
    btn2.pack(fill=tk.BOTH)


def design_middle(master):
    fr = tk.Frame(master, bg=white, padx=20, pady=20)
    fr.pack(expand=1, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(fr)
    global display_listbox
    display_listbox = tk.Listbox(fr, bg="#d1d1d1", yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    display_listbox.pack(expand=1, fill=tk.BOTH)

def design_bottom(master):
    hold_frame = tk.Frame(master, pady=20, bg=white)
    hold_frame.pack(fill=tk.BOTH)

    send_msg_box = tk.Entry(hold_frame)
    send_msg_box.pack(expand=True, side=tk.LEFT, fill=tk.BOTH)

    send_btn = tk.Button(hold_frame, text="SEND", width=10, command=client.send)
    send_btn.pack(side=tk.LEFT)

    return send_msg_box

def create_window():
    root = tk.Tk()
    root.geometry("800x800")
    root.protocol('WM_DELETE_WINDOW', lambda: cleanup(root))

    top_frame = tk.Frame(root, width=800, height=100, bg=white, padx=15, pady=15)
    display_frame = tk.Frame(root, width=800, height=600, bg=white,padx=15, pady=15)
    send_frame = tk.Frame(root, width=800, height=100, bg=white, padx=15, pady=15)

    top_frame.pack_propagate(0)
    top_frame.pack()
    display_frame.pack_propagate(0)
    display_frame.pack()
    send_frame.pack_propagate(0)
    send_frame.pack()

    design_top(root, top_frame)
    design_middle(display_frame)
    global msg_box
    msg_box = design_bottom(send_frame)

    return root

def IP_window():
    root = tk.Tk()
    root.geometry("200x200")
    l1 = tk.Label(root, text="Enter server IP", padx=20, pady=20)
    l1.pack()
    e = tk.Entry(root)
    e.pack()
    return root, e

server_IP = None
def get_IP(root, e):
    global server_IP
    server_IP = e.get()
    root.destroy()

if __name__ == "__main__":
    connected = False
    username = None
    while not connected:
        dialog, e = IP_window()
        b1 = tk.Button(dialog, text="Submit", command=lambda: get_IP(dialog, e))
        b1.pack()
        dialog.mainloop()

        if server_IP == "":
            server_IP = "127.0.0.1"
        server_port = 50000
        try:
            client.socket.connect((server_IP, server_port))
            client.socket.settimeout(None)
            username = input("Enter username: ")
            client.send(bytes(username, ENCODING))
            connected = True
        except:
            print("Could not connect to server with IP: %s!! Try Again." %(server_IP))


    receive_thread = Thread(target=client.receive)
    receive_thread.start()

    window = create_window()
    window.mainloop()
