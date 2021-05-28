import socket
import client

host = '0.0.0.0'
port = 5407

max_players = 4
client_list = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_data (sender, data):
    while True:
        for c in client_list:
            if c == sender:
                continue
            #sendata = bytearray(msg, 'utf8')
            stream.sendall(data)

with s:
    while len(client_list) < max_players:
        s.bind((host, port))
        s.listen()
        stream, address = s.accept()
        client = client.ClientHandler(stream, address)
        client_list.append(client)
        print('connection recieved from', address)

            