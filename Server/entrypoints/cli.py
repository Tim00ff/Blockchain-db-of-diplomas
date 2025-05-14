from ..core import BlockchainServer

def start_server():
    server = BlockchainServer()
    try:
        server.run()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nServer stopped gracefully")

if __name__ == "__main__":
    start_server()