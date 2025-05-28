import socket
import json
import argparse
import sys


class BlockClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def connect(self) -> socket.socket:
        """Establish a TCP connection to the server"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def send_command(self, command: str) -> dict:
        """
        Send a command to the server and parse the response
        Format: "COMMAND args\r\n\r\n"
        """
        try:
            with self.connect() as sock:
                # Format command with required line endings
                full_command = f"{command}\r\n\r\n"
                sock.sendall(full_command.encode('utf-8'))

                # Receive response (adjust buffer size as needed)
                response = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    # Check if we've received the complete response
                    if b"\r\n\r\n" in response or b"\n\n" in response:
                        break

                return self.parse_response(response.decode('utf-8'))

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def parse_response(self, response: str) -> dict:
        """Parse server response into structured format"""
        if not response:
            return {"status": "error", "message": "Empty response"}

        # Split into header and body
        parts = response.split('\n', 1)
        header = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""

        # Parse header
        header_parts = header.split(' ', 1)
        status = header_parts[0]
        command = header_parts[1] if len(header_parts) > 1 else ""

        # Parse JSON body if exists
        data = {}
        if body:
            try:
                data = json.loads(body.replace("'", '"'))
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                data = {"raw": body}

        return {
            "status": status,
            "command": command,
            "data": data['data']
        }

    def view_block(self, block_id: int) -> dict:
        """View a specific block from the blockchain"""
        return self.send_command(f"VIEW_BLOCK {block_id}")


def main():
    parser = argparse.ArgumentParser(description='Blockchain Client')
    parser.add_argument('--host', default='localhost', help='Server hostname')
    parser.add_argument('--port', type=int, default=65432, help='Server port')
    parser.add_argument('command', choices=['view_block'], help='Command to execute')
    parser.add_argument('block_id', type=int, nargs='?', default=0, help='Block ID to view')

    args = parser.parse_args()

    client = BlockClient(args.host, args.port)

    if args.command == "view_block":
        response = client.view_block(args.block_id)
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()