import selectors
import socket
import types
import threading

host = '192.168.1.5'
port = 5407

udp_port = 25011

clientlist = []
udpclientlist = []
server_int = 0

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

def accept_wrapper(sock):
    global server_int

    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)


    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    clientlist.append(conn)

    server_int_bytes = bytearray('server'+str(server_int), 'utf8')
    conn.sendall(server_int_bytes)
    server_int += 1

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
            for c in clientlist:
                if c == sock:
                    continue
                sent = c.send(data.outb) 
                data.outb = data.outb[sent:]

def udphandle ():
    while True:
        data, addr = udps.recvfrom(1024)
        if(addr not in udpclientlist):
            udpclientlist.append(addr)
        for c in udpclientlist:
            udps.sendto(data, c)

t1 = threading.Thread(target=udphandle, args=())
t1.start()

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)