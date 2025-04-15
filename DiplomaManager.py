import os
from typing import Dict, Optional
from faker import Faker
import random
from KeyManager import KeyManager
from DiplomaGenerator import DiplomaGenerator


class DiplomaManager:
    def __init__(self, key_manager: Optional[KeyManager] = None):
        self.diplomas: Dict[str, DiplomaGenerator] = {}
        self.key_manager = key_manager or KeyManager()
        self.fake = Faker('ru_RU')

        # Списки для генерации случайных данных
        self.qualifications = ['Бакалавр', 'Магистр', 'Специалист']
        self.specialties = [
            'Информационные системы',
            'Искусственный интеллект',
            'Кибербезопасность',
            'Разработка ПО'
        ]

    def create_random_diploma(self) -> str:
        """Создает случайный подписанный диплом и возвращает его ID"""
        data = {
            'institution': self.fake.company(),
            'full_name': self.fake.name(),
            'program': 'Программная инженерия',
            'qualification': random.choice(self.qualifications),
            'specialty': random.choice(self.specialties),
            'issue_date': self.fake.date_between(start_date='-5y', end_date='today').strftime('%d.%m.%Y'),
            'reg_number': f"{self.fake.year()}-BY-{self.fake.unique.random_number(digits=4)}",
            'rector_name': f"{self.fake.last_name()} {self.fake.first_name()[0]}.{self.fake.middle_name()[0]}.",
            'secretary_name': f"{self.fake.last_name()} {self.fake.first_name()[0]}.{self.fake.middle_name()[0]}."
        }

        diploma = DiplomaGenerator(data)
        diploma.create_signature(self.key_manager)
        self.diplomas[diploma.data['reg_number']] = diploma
        return diploma.data['reg_number']

    def get_diploma(self, diploma_id: str) -> Optional[DiplomaGenerator]:
        """Возвращает диплом по ID"""
        return self.diplomas.get(diploma_id)

    def get_all_diplomas(self) -> Dict[str, DiplomaGenerator]:
        """Возвращает все дипломы"""
        return self.diplomas

    def print_diploma(self, diploma_id: str, full_info: bool = True) -> None:
        """Выводит информацию о дипломе"""
        diploma = self.get_diploma(diploma_id)
        if not diploma:
            print(f"Диплом с ID {diploma_id} не найден")
            return

        if full_info:
            print(diploma.to_string())
            is_valid = diploma.verify(self.key_manager.public_key)
            print(f"\nПодпись {'валидна' if is_valid else 'недействительна'}")
        else:
            print(diploma.to_string().split('----------------------------------------')[0].strip())

    def export_diplomas(self, folder_path: str) -> None:
        """Экспортирует все дипломы в указанную папку"""
        os.makedirs(folder_path, exist_ok=True)
        for diploma_id, diploma in self.diplomas.items():
            with open(os.path.join(folder_path, f"{diploma_id}.txt"), 'w', encoding='utf-8') as f:
                f.write(diploma.to_string())

    def import_diplomas(self, folder_path: str) -> None:
        """Импортирует дипломы из папки"""
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                try:
                    diploma = DiplomaGenerator.from_file(os.path.join(folder_path, filename))
                    self.diplomas[diploma.data['reg_number']] = diploma
                except Exception as e:
                    print(f"Ошибка загрузки файла {filename}: {str(e)}")

    def print_all_diplomas(self, full_info: bool = True) -> None:
        """Выводит информацию обо всех дипломах"""
        for diploma_id in self.diplomas:
            self.print_diploma(diploma_id, full_info)
            print("\n" + "=" * 50 + "\n")


def display_menu():
    print("\n" + "=" * 50)
    print(" Diploma Management System ".center(50, '#'))
    print("=" * 50)
    print("1. Создать случайный диплом")
    print("2. Показать все дипломы")
    print("3. Показать конкретный диплом")
    print("4. Экспортировать дипломы в папку")
    print("5. Загрузить дипломы из папки")
    print("6. Проверить подпись диплома")
    print("7. Показать текущие ключи")
    print("8. Сохранить ключи в файл")
    print("9. Загрузить ключи из файла")
    print("10. Выход")
    print("=" * 50)
    return input("Выберите опцию (1-10): ")


def main():
    key_manager = KeyManager()
    manager = DiplomaManager(key_manager)

    while True:
        choice = display_menu()

        # Создание диплома
        if choice == '1':
            diploma_id = manager.create_random_diploma()
            print(f"\n[Успех] Создан диплом с ID: {diploma_id}")

        # Показать все дипломы
        elif choice == '2':
            print("\nСписок всех дипломов:")
            for idx, diploma_id in enumerate(manager.diplomas.keys(), 1):
                print(f"{idx}. {diploma_id}")

            if input("\nПоказать подробности? (y/n): ").lower() == 'y':
                manager.print_all_diplomas(full_info=True)

        # Показать конкретный диплом
        elif choice == '3':
            diploma_id = input("Введите ID диплома: ")
            if diploma_id in manager.diplomas:
                manager.print_diploma(diploma_id, full_info=True)
            else:
                print("[Ошибка] Диплом с таким ID не найден")

        # Экспорт
        elif choice == '4':
            folder = input("Введите путь для экспорта: ")
            try:
                manager.export_diplomas(folder)
                print(f"[Успех] Экспортировано {len(manager.diplomas)} дипломов")
            except Exception as e:
                print(f"[Ошибка] {str(e)}")

        # Импорт
        elif choice == '5':
            folder = input("Введите путь для импорта: ")
            if os.path.exists(folder):
                manager.import_diplomas(folder)
                print(f"[Успех] Загружено {len(manager.diplomas)} дипломов")
            else:
                print("[Ошибка] Папка не существует")

        # Проверка подписи
        elif choice == '6':
            diploma_id = input("Введите ID диплома: ")
            if diploma_id in manager.diplomas:
                is_valid = manager.diplomas[diploma_id].verify(key_manager.public_key)
                print(f"\nПодпись {'валидна' if is_valid else 'недействительна'}")
            else:
                print("[Ошибка] Диплом не найден")

        # Показать ключи
        elif choice == '7':
            print("\nОткрытый ключ:")
            print(key_manager.get_public_pem())
            print("\nЗакрытый ключ:")
            print(key_manager.get_private_pem())

        elif choice == '8':
            filename = input("Введите имя файла для сохранения ключей: ")
            try:
                manager.key_manager.save_to_file(filename)
                print(f"[Успех] Ключи сохранены в {filename}")
            except Exception as e:
                print(f"[Ошибка] Не удалось сохранить ключи: {str(e)}")

        elif choice == '9':
            filename = input("Введите имя файла для загрузки ключей: ")
            try:
                new_key_manager = KeyManager.from_file(filename)
                manager.key_manager = new_key_manager
                print(f"[Успех] Ключи загружены из {filename}")
            except Exception as e:
                print(f"[Ошибка] Не удалось загрузить ключи: {str(e)}")

        elif choice == '10':
            print("\nЗавершение работы...")
            break

        else:
            print("\n[Ошибка] Неверный выбор, попробуйте снова")


if __name__ == "__main__":
    main()