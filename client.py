import socket
import time
import threading

class ClientHandler (object):
    
    def __init__(self, stream, address):
        self.stream = stream
        self.address = address

    