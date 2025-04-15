from DiplomaManager import DiplomaManager, main as UI

from KeyManager import KeyManager
from DiplomaGenerator import DiplomaGenerator
from Blockchain import Blockchain
from BlockchainManager import BlockchainManager



def main():
    main_menu()

def genesis():
    # Инициализация KeyManager Genesis
    key_manager = KeyManager.from_file("Genesis/key.txt")
    # Загрузка данных диплома Genesis
    diploma = DiplomaGenerator.from_file("Genesis/g/2000-BY-9473.txt")
    # Инициализация блокчейна
    blockchain = Blockchain(
        path="Blockchain",
        diploma_data=diploma.to_dict(),
        public_key=key_manager.public_key
    )
    # Проверка цепочки
    if blockchain.validate_chain():
        print("Blockchain successfully initialized and validated!")
        blockchain.print_chain_info()
    else:
        print("Blockchain validation failed!")
    return blockchain


def main_menu():
    while True:
        print("\n=== Главное меню ===")
        print("1. Управление дипломами")
        print("2. Управление блокчейном")
        print("3. Выход")
        choice = input("Выберите опцию: ")

        if choice == '1':
            UI()
        elif choice == '2':
            initialize_blockchain()
        elif choice == '3':
            print("Завершение работы...")
            break
        else:
            print("Неверный выбор, попробуйте снова")


def initialize_blockchain():
    try:
        # Пытаемся загрузить существующий блокчейн
        blockchain = Blockchain()
    except ValueError:
        # Если блокчейн не существует, создаём новый с Genesis-блоком
        print("\nИнициализация нового блокчейна...")
        blockchain = genesis()

    # Запускаем UI для управления блокчейном
    BlockchainManager(blockchain).start()

if __name__ == "__main__":
    main()


