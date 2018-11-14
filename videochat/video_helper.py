from multiprocessing import Process,Queue,Pipe
import multiprocessing
import socket, videosocket
from videofeed import VideoFeed
from multiprocessing.reduction import ForkingPickler
import StringIO
import pickle
import Tkinter as tk

# multiprocessing.set_start_method('spawn') 
# root = tk.Tk()
endVideo = False
videofeed = None
vsock = None

def close():
    global endVideo, root
    endVideo = True
    # root.destroy()
    # root.quit()

# Window design
# btn_exit = tk.Button(root, text="Quit", command = lambda:close)
# btn_exit.pack()

def V_s_video():
		global root, endVideo
		try:
			while (endVideo == False):
				frame = vsock.vreceive()
				videofeed.set_frame(frame)
				frame = videofeed.get_frame()
				vsock.vsend(frame)
		except KeyboardInterrupt:
			sys.exit(0)

def V_c_video():
		global root,endVideo
		try:
			while (endVideo == False):
				frame = videofeed.get_frame()
				vsock.vsend(frame)
				frame = vsock.vreceive()
				videofeed.set_frame(frame)
		except KeyboardInterrupt:
			sys.exit(0)


def V_s(child_conn):
	global root, videofeed, vsock
	client_socket = pickle.loads(child_conn.recv())
	vsock = videosocket.videosocket(client_socket) # establish a video connection
	videofeed = VideoFeed(1,"A",1)
	# root.mainloop()
	V_s_video()
	

def V_c(child_conn):
	global root, videofeed, vsock
	client_socket = pickle.loads(child_conn.recv())
	vsock = videosocket.videosocket(client_socket) # establish a video connection
	videofeed = VideoFeed(1,"B",1)
	# root.mainloop()
	V_c_video()