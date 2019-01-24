'''
--TODO.0001: Make it so threads can close--
--TODO.0002: Make pong function--
--TODO.0003: Make Scan function--
TODO.0004: Make trade data function
TODO.0005: Make function that uses scan and trades data when it findsa new node.
TODO.0006: Make flood to build routing table algorithm
'''

import socket
import msgpack
import pprint
import threading
from contextlib import suppress

the_files = {'coolstuff.txt':'Hey, this is the contents of a cool text file', 'epic awesome music.mp3':'Not an actual MP3, but you get the idea'}

# Create our UDP socket and bind it to a random port on all interfaces
class Bot:
    def __init__(self,files,nd_id):
        self.file_contents = files
        self.nd_id = nd_id
        self.Ndx = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',0))
        print("Listening for peers on UDP port", self.sock.getsockname()[1])
        self.lstn = threading.Thread(target=self.__listen, args=())
        self.lstn.setDaemon(True)
        self.lstn.start()
        self.pingmsg = msgpack.packb({'msgtype':'ping','nodeid':self.nd_id,'msgid':1,'ddrp':'127.0.0.1','ddrsck':self.sock.getsockname()[1]})

        print(self.sock)
 
    def __pong(self,data,addr):
        reply_data = msgpack.packb({'msgtype':'pong', 'nodeid':self.nd_id, 'replyto':data['msgid'],'ddrp':'127.0.0.1','ddrsck':self.sock.getsockname()[1]},use_bin_type=True)
        self.sock.sendto(reply_data,addr)

    def ping(self,addr):
        self.sock.sendto(self.pingmsg,addr)

    def __listen(self):
        while True:
            in_data,in_addr = self.sock.recvfrom(65536)
            data = msgpack.unpackb(in_data, encoding='utf-8')

            tmp = data if isinstance(data,list) else [data]
            self.__pshNdx(tmp)

            #pprint.pprint((in_addr,data))
            print("I am node: ",self.nd_id)
            print("Known Nodes: ",self.Ndx)
            print(" ")

            if data['msgtype']=='ping':
                self.__pong(data, in_addr)

    def __pshNdx(self,d):
        n = 'nodeid'
        i=0
        j=0
        while i in range(len(self.Ndx)):
            while j in range(len(d)):
                #print("test: ",i,j,d)
                if self.nd_id == d[j][n]: d.pop(j)
                if len(d) > 0 and self.Ndx[i][n] == d[j][n]: d.pop(j)
                j+=1
            i+=1

        for i in d: self.Ndx.append({'nodeid':i['nodeid'],'ddrp':i['ddrp'],'ddrsck':i['ddrsck']})

    def scanPorts(self):
        l = [i for i in range(1,65535+1)]
        for i in l:
            try:
                #print('pinging port: ',i)
                self.ping(('127.0.0.1',i))
            except OSError:
                pass

node = []
for i in range(5):
    node.append(Bot({},i))

node[1].scanPorts()

# Test Network
# import P2PNet0001
# import msgpack
# node = P2PNet0001.FileShareNode({})
# pingmsg = msgpack.packb({'msgtype':'ping','msgid':1337})
# node.sock.sendto(pingmsg,('127.0.0.1',35795))
