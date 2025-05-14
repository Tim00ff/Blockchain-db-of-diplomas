# Server.py (основной модуль сервера)
import socket
import threading
from ServerInteract import process_client_request
from old_version.BlockchainManager import BlockchainManager


class Server:
    def __init__(self):
        self.blockchain_manager = BlockchainManager()
        self.block_queue = []
        self.rewards = {}
        self.lock = threading.Lock()
        self.miner_counter = 0
        self.miner_lock = threading.Lock()

    def handle_client(self, client_socket):
        buffer = ""
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data
                print(buffer)
                while "\r\n\r\n" in buffer:
                    request, sep, buffer = buffer.partition("\r\n\r\n")
                    response = process_client_request(
                        request,
                        self.blockchain_manager.blockchain,
                        self.block_queue,
                        self.rewards,
                        self.lock,
                        self.miner_counter
                    )
                    client_socket.sendall(response.encode('utf-8'))

        finally:
            client_socket.close()

    def start(self, host='127.0.0.1', port=65432):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print(f"Server listening on {host}:{port}")

            while True:
                client_sock, addr = s.accept()
                print(f"New connection from {addr}")
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=(client_sock,)
                )
                client_handler.start()