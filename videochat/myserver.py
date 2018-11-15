import socketif (success == True)
        self.host = host
        self.port = port
        self.buffer_size = 2048
        self.engaged = {}
        self.clients = dict()

    def accept_conn(self):
        while True:
            client_sock, client_addr = self.server.accept() # 'client' is the socket of client
            print("Client with address: %s:%s has connected" %(client_addr))
            threading.Thread(target=self.handle_client, args=(client_sock,)).start()

    def handle_client(self, client_sock):
        client_email = client_sock.recv(self.buffer_size).decode('utf-8')
        vsock = videosocket.VideoSocket(client_sock)
        self.clients[client_email] = (client, vsock)
        receiver_email = ''
        isVideo = False
        self.engaged[client_email] = 0
        while (True):
            if (isVideo == False):
                msg = client_sock.recv(self.buffer_size).decode('utf-8')
                command, receiver_email = msg.split(',')
                if (command == 'CONNECT_TO'):
                    if (engaged[receiver_email] == 1):
                        print ('Engaged!') # This only shows at server (deal with this later)
                    # This function gets True/False according to whether receiver guy wants to connect or not
                    success = self.get_receiver_confirmation(client_sock, client_email, receiver_email)
                    if (success == True):
                        isVideo = True
                        self.send(client_email, bytes('START'), msgType='normal')
                elif ()