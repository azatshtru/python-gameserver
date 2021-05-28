import socket
import threading

host = '0.0.0.0'
port = 5407

max_players = 4
client_list = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_data ():
    while True:
        msg = input()
        sendata = bytearray(msg, 'utf8')
        stream.sendall(sendata)

with s:
    s.bind((host, port))
    s.listen()
    stream, address = s.accept()
    with stream:
        print('connection recieved from', address)
        t1 = threading.Thread(target=send_data, args=())
        t1.start()
        while True:
            data = stream.recv(1024)
            if not data:
                break
            print(data.decode('utf8'))

            