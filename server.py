import socket
import time
import threading

host = '0.0.0.0'
port = 5407

max_players = 4
client_list = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_data (sender, data):
    for c in client_list:
        if c == sender:
            continue
        c.stream.sendall(data)

            
class ClientHandler (object):
    
    def __init__(self, stream, address):
        self.stream = stream
        self.address = address

        t1 = threading.Thread(target=self.recieve_data, args=())
        t1.start()

    def recieve_data (self):
        with self.stream:
            while True:
                data = self.stream.recv(1024)
                if not data:
                    break
                send_data(self, data)
                time.sleep(0.25)

with s:
    s.bind((host, port))
    while len(client_list) < max_players:
        s.listen()
        stream, address = s.accept()
        _client = ClientHandler(stream, address)
        client_list.append(_client)
        print('connection recieved from', address)

            