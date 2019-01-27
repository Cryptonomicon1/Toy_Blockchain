'''
--TODO.0001: Make it so threads can close--
--TODO.0002: Make pong function--
--TODO.0003: Make Scan function--
--TODO.0004: Make trade data function--
--TODO.0005: Make function that uses scan and trades data when it findsa new node.--
TODO.0006: Make flood to build routing table algorithm
--TODO.0007: Add blockchain to each node--
--TODO.0008: Add pshBlck function--
--TODO.0009: Make Nodes Share Blocks--
TODO.0010: Keep Each Node up2date on their blckchn
'''

import socket
import msgpack
import pprint
import threading
from contextlib import suppress
import hashlib as hsh
import random as r
from datetime import datetime as dt
import time as t

r.seed(a=None)

# Create our UDP socket and bind it to a random port on all interfaces
class Bot:
    def __init__(self,files,nd_id):
        self.file_contents = files
        self.nd_id = nd_id
        self.Ndx = []
        self.blk_bffr = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1',0))
        print("Node:", self.nd_id,"listening on port:", self.sock.getsockname()[1])
        self.lstn = threading.Thread(target=self.__listen, args=())
        self.lstn.setDaemon(True)
        self.lstn.start()
        self.chn_pshr = threading.Thread(target=self.__blkChnPshrDmn, args=())
        self.chn_pshr.setDaemon(True)
        self.chn_pshr.start()
        self.prt_cnt = 65535
        self.id_lst = [self.nd_id]
        self.blck_chn = [{'data':'1st blk','nonce':1,'datetime':'2019-01-27 09:35:46.817316','hash':hsh.md5(b'1st blk12019-01-27 09:35:46.817316').hexdigest()}]

        #print(self.sock) # Troubleshooting Tool
 
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
        elif isinstance(d,dict) and d[mt] == 'block':
            del d[mt]
            self.__pshBlkBffr(d)
        elif isinstance(d,list) and d[0][mt] == 'blockchain':
            self.__rplcBlkChn(d)

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

        if dlt_cnt > 0: #TShoot Tool
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

    def __mkBlkHsh(self, blk, lst_hsh):
        s = str(blk['data'])
        s += str(blk['nonce'])
        s += blk['datetime']
        s += lst_hsh
        return hsh.md5(s.encode()).hexdigest()

    def bldPshBlk(self, data):
        data = {'data':data}
        data['nonce'] = r.randint(1,1000)
        data['datetime'] = str(dt.now())
        data['hash'] = self.__mkBlkHsh(data, self.blck_chn[-1]['hash'])
        self.__bCstBlk(data)
        t.sleep(1)
        self.__pshBlkBffr(data)

    def __pshBlk(self, blk):
        if blk != self.blck_chn[-1]:
            self.blck_chn.append(blk)

    def __rplcBlkChn(self, chn):
        if len(chn) > len(self.blck_chn):
            del chn[0]['msgtype']
            self.blck_chn = chn

    def __bCstBlk(self, blk):
        blk['msgtype'] = 'block'
        m = msgpack.packb(blk,use_bin_type=True)
        for i in self.Ndx:
            self.sock.sendto(m, (i['ddrp'], i['ddrsck']))
            
    def __bCstBlkChn(self, chn):
        chn[0]['msgtype'] = 'blockchain'
        m = msgpack.packb(chn,use_bin_type=True)
        for i in self.Ndx:
            self.sock.sendto(m, (i['ddrp'], i['ddrsck']))

    def __pshBlkBffr(self, blk):
        if blk not in self.blk_bffr:
            self.blk_bffr.append(blk)

    def __blkChnPshrDmn(self):
        while True:
            i = 0
            while i in range(len(self.blk_bffr)):
                blk_hsh = self.blk_bffr[i]['hash']
                ndd_hsh = self.__mkBlkHsh(self.blk_bffr[i], self.blck_chn[-1]['hash'])
                if blk_hsh == ndd_hsh:
                    self.__pshBlk(self.blk_bffr[i])
                    del self.blk_bffr[i]
                else:
                    i+=1
            t.sleep(0.25)

# Testing Portion of the code.
# Everything below can be deleted

print(' ')
print("Building Nodes")
node = []
i = 0
for i in range(5):
    node.append(Bot({},i))

print(' ')
print("Nodes are finding each other.")
node[0].scnPrts()

# Troubleshooting Tool
for i in range(len(node)):
    for j in range(len(node[i].Ndx)):
        print('Node:',i,'found',node[i].Ndx[j]['nodeid'],'@',node[i].Ndx[j]['ddrsck'])
    print(' ')

d = 1
tmp = "Alice -> Bill 5 Chunky Monkeys"
print("Pushing", tmp,"onto Block Chain")
node[0].bldPshBlk(tmp)

tmp = "Alice -> Bill 3 Chunky Monkeys"
print("Pushing", tmp,"onto Block Chain")
node[3].bldPshBlk(tmp)

tmp = "Bill -> Alice 2 Chunky Monkeys"
print("Pushing", tmp,"onto Block Chain")
node[0].bldPshBlk(tmp)

tmp = "Bill -> Charlie 10 Chunky Monkeys"
print("Pushing", tmp,"onto Block Chain")
node[3].bldPshBlk(tmp)
t.sleep(4)

for i in range(len(node)):
    print(' ')
    print('Node: ', node[i].nd_id)
    for j in node[i].blck_chn:
        print(j['data'], j['hash'])
