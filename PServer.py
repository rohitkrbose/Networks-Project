import socket
import threading
import videosocket
from config import *

class Server:
    def __init__(self, host='', port=50000):
        self.server = socket.socket()
        self.server.bind((host, port))
        self.host = host
        self.port = port
        self.buffer_size = 2048
        self.clients = dict()

    def accept_conn(self):
        while True:
            client, client_addr = self.server.accept()
            print("Client with address: %s:%s has connected" %(client_addr))
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        username = client.recv(self.buffer_size).decode(ENCODING)
        vsock = videosocket.VideoSocket(client)
        self.clients[username] = (client, vsock)
        is_video = False
        receiver_username = None

        while True:
            if is_video:
                frame_bytes = vsock.vreceive()
                self.send_to_one(receiver_username, frame_bytes)
            else:
                msg = client.recv(self.buffer_size)
                if msg == bytes("QUIT", ENCODING):
                    client.close()
                    del self.clients[username]
                    self.broadcast(None, bytes("Client %s left the conversation" %(username), ENCODING))
                elif msg == bytes("VIDEO_CALL_START", ENCODING):
                    print("Video call initiated by %s" %(username))
                    # send all online users to the initiator of video call
                    self.send_online_users(username)

                    # receive the username client selected
                    receiver_username = client.recv(self.buffer_size).decode(ENCODING)
                    if receiver_username == "VIDEO_CALL_ABORT":
                        continue
                    print("Video call to: %s" %(receiver_username))

                    # send video call request to receiving target
                    success = self.get_receiver_confirmation(client, username, receiver_username)

                    if success:
                        is_video = True
                        # send acceptance message to initiator
                        self.send_to_one(username, bytes("VIDEO_CALL_START", ENCODING), is_video=False)
                elif msg == bytes("VIDEO_CALL_REJECTED", ENCODING) or msg == bytes("VIDEO_CALL_ACCEPT", ENCODING):
                    target_name = client.recv(self.buffer_size).decode(ENCODING)
                    self.send_to_one(target_name, msg, False)
                else:
                    # normal msg, broadcast to all
                    self.broadcast(username, msg.decode(ENCODING))

    def get_receiver_confirmation(self, client, source, target):
        '''
        Gets confirmation of whether target is willing to accept a video call
        '''
        print("Getting confirmation from %s for %s" %(target, source))
        req_msg = bytes("VIDEO_CALL_REQUEST", ENCODING)
        self.send_to_one(target, req_msg, False)
        from_uname = bytes(source, ENCODING)
        self.send_to_one(target, from_uname, False)

        confirmation = client.recv(self.buffer_size).decode(ENCODING)
        if confirmation == "VIDEO_CALL_ACCEPT":
            return True
        elif confirmation == "VIDEO_CALL_ABORT":
            return False

    def send_online_users(self, initiator_username):
        '''
        Send all online users separated by $ to initiator
        '''
        users = ""
        for u in self.clients.keys():
            if u != initiator_username:
                users = users + u + "$"
        msg = bytes(users, ENCODING)
        self.send_to_one(initiator_username, msg, False)

    def broadcast(self, sender, msg):
        for u, c in self.clients.items():
            if sender:
                c[0].send(bytes("%s: %s" %(sender, msg), ENCODING))
            else:
                c[0].send(bytes("%s" %(msg), ENCODING))

    def send_to_one(self, target, msg, is_video=True):
        c = self.clients[target]
        if is_video:
            c[1].vsend(msg)
        else:
            print("Message sent to %s" %(target))
            c[0].send(msg)

if __name__ == "__main__":
    s = Server()
    s.server.listen(10)
    print("Server is ON. Waiting for clients to connect!!!")
    accept_thread = threading.Thread(target=s.accept_conn)
    accept_thread.start()
    accept_thread.join()
    s.server.close()
