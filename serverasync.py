import selectors
import socket
import types
import threading

host = '192.168.1.7'
port = 5407
udp_port = 25011

server_int = 0
current_room = None
roomlist = []

sel = selectors.DefaultSelector()
# ...
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udps.bind((host, udp_port))

class Room(object):
    def __init__(self):
        self.clientlist = []

    def addclient(self, c):
        self.clientlist.append(c)

    def getlist(self):
        return self.clientlist

class Client(object):
    def __init__(self, stream, address, room):
        self.stream = stream
        self.address = address
        self.udpaddr = address
        self.room = room

    def setudp(self, udpaddr):
        self.udpaddr = udpaddr

def accept_wrapper(sock):
    global server_int
    global current_room

    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)

    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    if server_int == 0:
        room = Room()  
        roomlist.append(room)
        current_room = room

    server_int_bytes = bytearray('server'+str(server_int), 'utf8')
    conn.sendall(server_int_bytes)
    server_int += 1

    _client = Client(conn, addr, current_room)
    current_room.clientlist.append(_client)

    if server_int >= 2:
        server_int = 0


def get_sock_cl(conn):
    cur_room = None
    for room in roomlist:
        cur_room = room
        for c in room.getlist():
            if conn == c.stream:
                break
    return cur_room

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb = recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            #print('echoing', repr(data.outb), 'to', data.addr)
            for c in get_sock_cl(sock).getlist():
                if c.stream == sock:
                    continue
                sent = c.stream.send(data.outb) 
                data.outb = data.outb[sent:]

def add_udpaddr_cl(addr):
    cur_room = None
    for room in roomlist:
        cur_room = room
        for c in room.getlist():
            if addr[0] == c.address[0]:
                c.setudp(addr)
                break
    return cur_room

def udphandle ():
    while True:
        try:
            data, addr = udps.recvfrom(1024)
            room = add_udpaddr_cl(addr)
            if(room == None): continue
            for c in room.getlist():
                udps.sendto(data, c.udpaddr)
        except:
            udphandle ()

t1 = threading.Thread(target=udphandle, args=())
t1.start()

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)