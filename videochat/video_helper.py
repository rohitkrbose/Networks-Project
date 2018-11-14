from multiprocessing import Process,Queue,Pipe
import socket, videosocket
from videofeed import VideoFeed

def V ():
	client_sock = child_conn.recv()
	vsock = videosocket.videosocket(client_socket) # establish a video connection
    videofeed = VideoFeed(1,"A",1)
    while True:
        frame = vsock.vreceive()
        videofeed.set_frame(frame)
        frame = videofeed.get_frame()
        vsock.vsend(frame)