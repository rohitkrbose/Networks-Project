import socket, videosocket
import sys
import threading
from videofeed import VideoFeed

class Dummy:
    def __init__(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", port))
        self.server_socket.listen(5)
        self.usertoAdd = dict()
        self.AddtoUser = dict()
        self.usertoThread = dict()
        self.free = []
        self.buff_size = 2048

        # VideoFeed is not needed
        # self.videofeed = VideoFeed(1,"server",1)
        print "TCPServer Waiting for client on port ", port

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print "I got a connection from ", address

            address = address[0]
            th = threading.Thread(target = self.handleCommand, args = (client_socket, address))
            self.usertoThread[address] = th
            th.start()
            # CONNECTME,U_NAME
            # CONNECT,TARGET
            # DISCONNECT_ME,name

    def handleCommand(self, client_socket, address):
        while True:
            try:
                msg = client_socket.recv(self.buff_size)
                msg = msg.decode('utf-8')
                print(msg)
                command, name = msg.split(',')
            except Exception as e:
                print e
            
            # To send: a confirmation optional
            if command == "CONNECTME":
                print("Connect me statement")
                if name not in self.usertoAdd:
                    print "Adding user, address: ", name, address
                    self.usertoAdd[name] = address
                    self.AddtoUser[address] = name

                # This user is now free, either at the beginning, or at the end due to trigger by q
                self.free.append(name)
                to_send = "ACCEPTING YOU"

            # DISCUSS
            elif command == "DISCONNECTME":
                print("Disconnect me from server")
                self.usertoAdd.pop(name)
                self.AddtoUser.pop(address)
                self.free.remove(name)

            elif command == "CONNECT":
                # He sends to server, server sends a simple IP
                print "CONNECT to user: ", name

                for elem in self.usertoAdd:
                    print elem

                if name not in self.usertoAdd:
                    to_send = "NOT AVAILABLE"
                
                elif name not in self.free:
                    to_send = "BUSY"

                else:
                    to_send = str(self.usertoAdd[name])
                    self.free.remove(name)
                    self.free.remove(self.AddtoUser[address])

            print "To SEND: ",to_send
                    
            client_socket.send(to_send.encode('utf-8'))

        del self.usertoThread[address]

if __name__ == "__main__":
    server = Dummy(int(sys.argv[1]))
    server.start()
