from multiprocessing import Process,Queue,Pipe
import socket, videosocket
from videofeed import VideoFeed
from multiprocessing.reduction import ForkingPickler
import StringIO
import pickle

def V ():
	client_sock = pickle.loads(child_conn.recv())
	vsock = videosocket.videosocket(client_socket) # establish a video connection
	videofeed = VideoFeed(1,"A",1)
	while True:
		frame = vsock.vreceive()
		videofeed.set_frame(frame)
		frame = videofeed.get_frame()
		vsock.vsend(frame)