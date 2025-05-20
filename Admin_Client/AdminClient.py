import socket
import json
from KeyManager import KeyManager
from DiplomaGenerator import DiplomaGenerator


class BlockchainClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.key_manager = None
        self.logged_in = False
        self.username = None
        self.password = None

    def connect(self):
        """Установить соединение с сервером"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def send_command(self, command: str) -> dict:
        """Отправить команду и получить ответ"""
        try:
            with self.connect() as sock:
                sock.sendall(command.encode('utf-8'))
                response = sock.recv(4096).decode('utf-8')
                return self.parse_response(response)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def login(self, username: str, password: str) -> dict:
        """Отправить команду логина"""
        command = f"LOGIN {username} {password}\r\n\r\n"
        self.username = username
        self.password = password
        return self.send_command(command)

    @staticmethod
    def parse_response(response: str) -> dict:
        """Парсинг ответа сервера"""
        lines = (response.strip().split('\r\n'))
        if not lines:
            return {"status": "error", "message": "Empty response"}

        status_line = lines[0].split(' ', 2)
        result = {
            "status": status_line[0],
            "code": str(status_line[1]) if len(status_line) > 1 else None,
            "message": status_line[2] if len(status_line) > 2 else None,
            "data": {}
        }

        if len(lines) > 1 and lines[1]:
            try:
                result["data"] = json.loads(lines[1])
            except json.JSONDecodeError:
                result["data"] = lines[1]

        return result


def print_header():
    print("\n╔══════════════════════════════╗")
    print("║   Admin Client wth Diplomas  ║")
    print("╚══════════════════════════════╝")


def input_with_retry(prompt, required=True, is_password=False):
    """Ввод данных с повторением при ошибке"""
    while True:
        try:
            if is_password:
                value = input(prompt).strip()
            else:
                value = input(prompt).strip()

            if required and not value:
                print("Это поле обязательно для заполнения!")
                continue

            return value
        except KeyboardInterrupt:
            print("\nОтмена ввода")
            raise
        except Exception as e:
            print(f"Ошибка ввода: {str(e)}")


def main():
    print_header()

    # Настройка подключения
    host = input_with_retry("Введите адрес сервера [localhost]: ", required=False) or "localhost"
    port = int(input_with_retry("Введите порт сервера [65432]: ", required=False) or 65432)

    client = BlockchainClient(host, port)

    # Аутентификация
    print("\n🔐 Аутентификация")
    while True:
        username = input_with_retry("Имя пользователя: ")
        password = input_with_retry("Пароль: ", is_password=True)

        response = client.login(username, password)
        print(response)
        if response.get("status") == "OK":
            client.logged_in = True
            client.username = username
            print("\n✅ Успешный вход в систему!")
            break
        else:
            print("\n❌ Ошибка аутентификации!")
            print(f"Причина: {response.get('message', 'Неизвестная ошибка')}")
            if input("Повторить попытку? (y/n): ").lower() != 'y':
                return

    # Управление ключами
    print("\n🔑 Управление ключами:")
    print("1. Создать новую пару ключей")
    print("2. Использовать существующие ключи")
    choice = input_with_retry("Выберите действие [1/2]: ")

    if choice == "1":
        key_path = input_with_retry("Введите путь для сохранения ключей: ")
        KeyManager().save_to_file(key_path)
        client.key_manager = KeyManager.from_file(key_path)
        print(f"✅ Ключи успешно созданы и сохранены в {key_path}")
    else:
        key_path = input_with_retry("Введите путь к файлу ключей: ")
        client.key_manager = KeyManager.from_file(key_path)
        print("✅ Ключи успешно загружены")

    # Создание диплома
    print("\n🎓 Создание диплома:")
    diploma_data = {
        'full_name': input_with_retry("ФИО студента: "),
        'institution': input_with_retry("Учебное заведение: "),
        'qualification': input_with_retry("Степень (Бакалавр/Магистр и т.д.): "),
        'specialty': input_with_retry("Специальность: "),
        'issue_date': input_with_retry("Дата выдачи (ДД.ММ.ГГГГ): "),
        'reg_number': input_with_retry("Регистрационный номер: "),
        'program': input_with_retry("Образовательная программа: "),
        'rector_name': input_with_retry("ФИО ректора (Иванов И.И.): "),
        'secretary_name': input_with_retry("ФИО секретаря (Петров П.П.): ")
    }

    # Создание и подпись диплома
    try:
        diploma = DiplomaGenerator(diploma_data)
        diploma.create_signature(client.key_manager)
    except Exception as e:
        print(f"❌ Ошибка создания диплома: {str(e)}")
        return

    # Формирование команды
    command_data = {
        "diploma_data": diploma.to_dict(),
        "public_key": client.key_manager.get_public_pem(),
        "signature": diploma.data['signature']
    }

    command = f"LOGIN {username} {password}\r\nADD_BLOCK {json.dumps(command_data)}\r\n\r\n"

    # Отправка команды
    print("\n🚀 Отправка данных на сервер...")
    response = client.send_command(command)
    print(response)
    # Обработка ответа
    if response[0:1] == "OK":
        print("\n✅ Успешно!")
        print(f"Хэш: {response['data'].get('initial_hash', 'N/A')}")
        print(f"Сложность: {response['data'].get('difficulty', 'N/A')}")
    else:
        print("\n❌ Ошибка!")
        print(f"Код: {response.get('code', 'Unknown')}")
        print(f"Сообщение: {response.get('message', 'Unknown error')}")
        if 'data' in response:
            print(f"Детали: {response['data']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nРабота прервана пользователем")
    finally:
        print("\nРабота программы завершена. Нажмите Enter для выхода...")
        input()