import socket
from socket import timeout

class videosocket:
    '''A special type of socket to handle the sending and receiveing of fixed
       size frame strings over ususal sockets
       Size of a packet or whatever is assumed to be less than 100MB
    '''

    def __init__(self , sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(10)

    def connect(self,host,port):
        self.sock.connect((host,port))

    def vsend(self, framestring):
        totalsent = 0
        metasent = 0
        length = len(framestring)
        lengthstr = str(length).zfill(8)

        while metasent < 8 :
            try:
                sent = self.sock.send(lengthstr[metasent:])
            except timeout:
                return (None)
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            metasent += sent
        
        
        while totalsent < length :
            try:
                sent = self.sock.send(framestring[totalsent:])
            except timeout:
                return (None)
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent += sent

    def vreceive(self):
        totrec=0
        metarec=0
        msgArray = []
        metaArray = []
        while metarec < 8:
            try:
                chunk = self.sock.recv(8 - metarec)
            except timeout:
                return (None)
            if chunk == '':
                raise RuntimeError("Socket connection broken")
            metaArray.append(chunk)
            metarec += len(chunk)
        lengthstr= ''.join(metaArray)
        length=int(lengthstr)

        while totrec<length :
            try:
                chunk = self.sock.recv(length - totrec)
            except timeout:
                return (None)
            if chunk == '':
                raise RuntimeError("Socket connection broken")
            msgArray.append(chunk)
            totrec += len(chunk)
        return ''.join(msgArray)

   


        
