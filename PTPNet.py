'''
--TODO.0001: Make it so threads can close--
--TODO.0002: Make pong function--
--TODO.0003: Make Scan function--
--TODO.0004: Make trade data function--
--TODO.0005: Make function that uses scan and trades data when it findsa new node.--
TODO.0006: Make flood to build routing table algorithm
TODO.0007: 

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
        self.sock.bind(('127.0.0.1',0))
        print("Listening for peers on UDP port", self.sock.getsockname()[1])
        self.lstn = threading.Thread(target=self.__listen, args=())
        self.lstn.setDaemon(True)
        self.lstn.start()
        self.prt_cnt = 65535
        self.id_lst = [self.nd_id]

        print(self.sock)
 
    def __pong(self,data,addr):
        reply_data = msgpack.packb({'msgtype':'pong', 'nodeid':self.nd_id, 'replyto':data['msgid'],'ddrp':'127.0.0.1','ddrsck':self.sock.getsockname()[1]},use_bin_type=True)
        self.sock.sendto(reply_data,addr)

    def ping(self,addr):
        pingmsg = msgpack.packb({'msgtype':'ping','nodeid':self.nd_id,'msgid':1,'ddrp':'127.0.0.1','ddrsck':self.sock.getsockname()[1]})
        self.sock.sendto(pingmsg,addr)

    def __listen(self):
        while True:
            in_data,in_addr = self.sock.recvfrom(65536)
            data = msgpack.unpackb(in_data, encoding='utf-8')

            hndl = threading.Thread(target=self.__hndlPckTyp, args=(data, in_addr))
            hndl.start()
            '''
            # Trouble Shooting Tool
            print("Node: ",self.nd_id)
            print("Known Nodes: ",self.Ndx)
            print(" ")
            '''
    def __hndlPckTyp(self, d, a):
        mt = 'msgtype'
        #print('node: ',self.nd_id,' ',d) #Tshoot Tool
        if isinstance(d,dict) and d[mt] == 'ping':
            self.__chckPshNdx([d])
            self.__pong(d, a)
        elif isinstance(d,dict) and d[mt] == 'pong':
            self.__chckPshNdx([d])
        elif isinstance(d,list) and d[0][mt] == 'index':
            self.__chckPshNdx(d)

    def __chckPshNdx(self, d, n='nodeid'):
        for i in self.Ndx:
            if i[n] not in self.id_lst: self.id_lst.append(i[n])

        self.__pshNdx(d)

    def __pshNdx(self, d, n='nodeid'):
        dlt_cnt = len(self.Ndx)
        for i in d:
            if i[n] not in self.id_lst:
                self.Ndx.append({n:i[n],'ddrp':i['ddrp'],'ddrsck':i['ddrsck']})
        dlt_cnt = len(self.Ndx) - dlt_cnt

        if '''len(self.Ndx) < 7 and''' dlt_cnt > 0: #TShoot Tool
            self.__bCstNdx(self.Ndx)

    def __bCstNdx(self, ndx, n='nodeid'):
        ndx[0]['msgtype'] = 'index'
        m = msgpack.packb(ndx,use_bin_type=True)
        for i in ndx:
            if self.nd_id != i[n]:
                self.sock.sendto(m, (i['ddrp'], i['ddrsck']))

    def scnPrts(self):
        l = [i for i in range(1,self.prt_cnt+1)]
        for i in l:
            try:
                #print('pinging port: ',i) #Trouble Shooting Tool
                self.ping(('127.0.0.1',i))
            except OSError:
                pass

node = []
i = 0
for i in range(5):
    node.append(Bot({},i))

node[0].scnPrts()

for i in range(len(node)):
    print('Node: ',i,': ',node[i].Ndx)
