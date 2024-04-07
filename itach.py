import socket


class ItachClient:
    def __init__(self, host, port, client_type):
        self.svr_host = host
        self.svr_port = port
        self.client_type = client_type
        self.client = None

    def connect(self):
        # Get a new socket if you don't have one.
        if self.client is None:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.svr_host, self.svr_port))
