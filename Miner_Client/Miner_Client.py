import socket
import json
import getpass
import hashlib
from threading import Thread
from time import sleep
from time import time as current_time


class MinerClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.username = None
        self.password = None
        self.current_task = None
        self.mining = False
        self.check_interval = 30
        self.last_check = int(current_time())

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def send_command(self, command: str) -> dict:
        """Отправка команды с автоматическим добавлением LOGIN"""
        if not self.username or not self.password:
            return {"status": "error", "message": "Credentials not set"}

        full_command = f"LOGIN {self.username} {self.password}\r\n{command}\r\n\r\n"
        try:
            with self.connect() as sock:
                sock.sendall(full_command.encode('utf-8'))
                response = sock.recv(4096).decode('utf-8')
                return self.parse_response(response)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def login(self) -> dict:
        """Отправка команды с автоматическим добавлением LOGIN"""
        if not self.username or not self.password:
            return {"status": "error", "message": "Credentials not set"}

        full_command = f"LOGIN {self.username} {self.password}\r\n\r\n"
        try:
            with self.connect() as sock:
                sock.sendall(full_command.encode('utf-8'))
                response = sock.recv(4096).decode('utf-8')
                return self.parse_response(response)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def parse_response(response: str) -> dict:
        lines = response.strip().split('\r\n')
        if not lines:
            return {"status": "error", "message": "Empty response"}

        status_line = lines[0].split(' ', 2)
        data = {}
        if len(lines) > 1 and lines[1]:
            try:
                data = json.loads(lines[1], strict=False)["data"]
            except json.JSONDecodeError as e:
                data = {lines[1]}
        return {
            "status": status_line[0],
            "code": status_line[1] if len(status_line) > 1 else None,
            "data": data
        }

    def start_mining(self):
        self.mining = True
        Thread(target=self._mining_loop, daemon=True).start()

    def _mining_loop(self):
        while self.mining:

            if int(current_time()) - self.last_check > self.check_interval:
                self._check_task_status()
                self.last_check = int(current_time())

            if not self.current_task:
                self._get_task()


            if self.current_task:
                self._process_task()


            sleep(0.1)

    def _check_task_status(self):
        """Проверка, актуальна ли текущая задача"""
        if not self.current_task:
            return

        response = self.send_command(f"VIEW_BLOCK {self.current_task['block_id']}")
        if response.get("status") == "OK":
            print("[INFO] Блок уже добавлен в блокчейн, задача отменена")
            self.current_task = None

    def _get_task(self):
        """Получение новой задачи"""
        response = self.send_command("MINE")
        if response.get("status") == "OK":
            new_task = response.get("data")
            print(response)
            if self.current_task and new_task["block_id"] != self.current_task["block_id"]:
                print("[INFO] Обнаружена новая задача, сброс текущей")
                self.current_task = None
            self.current_task = new_task
            print(f"[TASK] Новая задача: Блок #{self.current_task['block_id']}")
            print(f"Диапазон: {self.current_task['nonce_start']}-{self.current_task['nonce_end']}")
            print(f"Сложность: {self.current_task['difficulty']} нулей")
        elif response.get("status") == "ERROR" and response.get("code") == "401":
            print("No tasks are currently pending\n")


    def _calculate_hash(self, nonce: int) -> str:
        task_data = self.current_task
        data_string = (
                task_data["info"] +
                str(nonce) +
                str(task_data["difficulty"])
        )
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    def _process_task(self):
        start = self.current_task["nonce_start"]
        end = self.current_task["nonce_end"]
        target_zeros = self.current_task["difficulty"]  # Number of leading zeros required

        print(f"[MINING] Processing range {start}-{end}")

        for nonce in range(start, end + 1):
            if not self.mining:
                break

            current_hash = self._calculate_hash(nonce)
            if current_hash.startswith('0' * target_zeros):
                print(f"[SOLUTION] Valid nonce found: {nonce}")
                self._submit_solution(nonce, current_hash)
                self.current_task = None
                return

        print("[WARNING] No valid nonce found in range")
        self.current_task = None  # Reset task to become idle

    def _submit_solution(self, nonce: int, solution_hash: str):
        response = self.send_command(f"SUBMIT_SOLUTION {nonce} {solution_hash}")
        if response.get("status") == "OK":
            print(f"[SUCCESS] Блок #{response['data']['block_id']} принят")
            print(f"Награда: {response['data'].get('reward', 0)}")
        else:
            print(f"[ERROR] {response.get('message', 'Unknown error')}")


def main():
    print("\n=== Blockchain Miner ===")
    host = input("Адрес сервера [localhost]: ") or "localhost"
    port = int(input("Порт сервера [65432]: ") or 65432)
    client = MinerClient(host, port)

    # Аутентификация
    print("\n=== Аутентификация ===")
    while True:
        username = input("Имя пользователя: ")
        password = input("Пароль: ")
        client.username = username
        client.password = password

        # Проверка учетных данных
        response = client.login()
        print(response)
        if response.get("status") == "OK":
            print("\nУспешный вход!")
            break
        print("\nОшибка аутентификации!")

    # Запуск майнинга
    client.start_mining()
    print("\nМайнинг запущен...")
    print("Нажмите Ctrl+C для остановки")

    try:
        while True: sleep(1)
    except KeyboardInterrupt:
        client.mining = False
        print("\nМайнинг остановлен")


if __name__ == "__main__":
    main()