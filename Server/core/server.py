import socket
import threading
from .request_router import RequestRouter
from ..models import Blockchain


class BlockchainServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = None
        self.lock = threading.Lock()
        self.rewards = {}
        self.blockchain = Blockchain()
        self.task_queue = []
        self.router = RequestRouter(
            blockchain=self.blockchain,
            task_queue=self.task_queue,
            rewards=self.rewards,
            lock=self.lock
        )

    def handle_client(self, client_socket):
        try:
            buffer = ""
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data
                print(buffer)
                while "\r\n\r\n" in buffer:
                    request, sep, buffer = buffer.partition("\r\n\r\n")
                    response = self.router.route_request(request)
                    client_socket.sendall(response.encode('utf-8'))
        finally:
            client_socket.close()

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f"Server running on {self.host}:{self.port}")

        while True:
            client_sock, addr = self.socket.accept()
            print(f"New connection from {addr}")
            client_handler = threading.Thread(
                target=self.handle_client,
                args=(client_sock,)
            )
            client_handler.start()

    def shutdown(self):
        self.socket.close()
        print("Server shutdown complete")