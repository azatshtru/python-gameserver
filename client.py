import socket
import time
import threading

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
                #server.send_data(self, data)
                time.sleep(0.25)