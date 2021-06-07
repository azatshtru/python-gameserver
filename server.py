import socket
import time
import threading

host = '0.0.0.0'
port = 5407

udp_port = 25011

max_players = 2
client_list = []
server_int = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udps.bind((host, udp_port))

def send_data (sender, data):
    for c in client_list:
        if c == sender:
            continue
        c.stream.sendall(data)

def udpsend (sender, data):
    for c in client_list:
        if c == sender:
            continue
        udps.sendto(data, c.udpaddr)

class ClientHandler (object):
    
    def __init__(self, stream, address):
        self.stream = stream
        self.address = address
        self.udpaddr = address

        t1 = threading.Thread(target=self.recieve_data, args=())
        t1.start()

        t_udp = threading.Thread(target=self.recieve_data_udp, args=())
        t_udp.start()

    def recieve_data (self):
        with self.stream:
            while True:
                data = self.stream.recv(1024)
                if not data:
                    break
                send_data(self, data)
                time.sleep(0.01)

    def recieve_data_udp (self):
        try:
            while True:
                data, addr = udps.recvfrom(1024)
                self.udpaddr = addr
                udpsend(self, data)
                #time.sleep(0.01)
        except:
            self.recieve_data_udp()

with s:
    s.bind((host, port))
    while len(client_list) < max_players:
        s.listen()
        stream, address = s.accept()

        server_int_bytes = bytearray('server'+str(server_int), 'utf8')
        stream.sendall(server_int_bytes)
        server_int += 1

        _client = ClientHandler(stream, address)
        client_list.append(_client)
        print('connection recieved from', address)
    print("Room full! Create new room for more players.")
            