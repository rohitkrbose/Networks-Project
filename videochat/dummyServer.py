import socket, videosocket
from videofeed import VideoFeed

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", 6000))
        self.server_socket.listen(5)
        self.usertoAdd = dict()
        self.AddtoUser = dict()
        self.free = []

        # VideoFeed is not needed
        # self.videofeed = VideoFeed(1,"server",1)
        print "TCPServer Waiting for client on port 6000"

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print "I got a connection from ", address

            # CONNECTME,U_NAME
            # CONNECT,TARGET
            # DISCONNECT_ME,name

            msg = client_socket.recv().decode('utf-8')
            command, name = msg.split(',')
            
            # To send: a confirmation optional
            if command == "CONNECTME":
                print("Connect me statement")
                if name not in self.usertoAdd:
                    self.usertoAdd[name] = address
                    self.AddtoUser[address] = name

                # This user is now free, either at the beginning, or at the end due to trigger by q
                self.free.append(name)

            # DISCUSS
            elif command == "DISCONNECTME":
                print("Disconnect me from server")
                self.usertoAdd.pop(name)
                self.AddtoUser.pop(address)
                self.free.remove(name)

            elif command == "CONNECT":
                # He sends to server, server sends a simple IP
                if name not in self.usertoAdd:
                    to_send = bytes("NOT AVAILABLE",'utf-8')
                
                elif name not in self.free:
                    to_send = bytes("BUSY", 'utf-8')

                else:
                    to_send = bytes(str(self.usertoAdd[name]), 'utf-8')
                    self.free.remove(name)
                    self.free.remove(self.AddtoUser[address])
                    
            client_socket.send(to_send)



if __name__ == "__main__":
    server = Server()
    server.start()
