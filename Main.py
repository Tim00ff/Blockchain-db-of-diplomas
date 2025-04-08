from Blockchain import Blockchain
from Diploma import DiplomaGenerator
from KeyManager import KeyManager
# Инициализация
test = Blockchain()
key_manager = KeyManager()  # Создаем менеджер ключей

# Создание диплома
diploma_data = {
    'institution': 'Государственный университет информатики',
    'full_name': 'Иванов Иван Иванович',
    'program': 'Программная инженерия',
    'qualification': 'Бакалавр',
    'specialty': 'Информационные системы',
    'issue_date': '01.06.2024',
    'reg_number': '2024-BY-1234',
    'rector_name': 'Петров П.П.',
    'secretary_name': 'Сидорова А.А.'
}

ivan_dip = DiplomaGenerator(diploma_data)
ivan_dip.create_signature(key_manager)  # Создаем подпись

# Получаем текстовое представление
diploma_text = DiplomaGenerator.from_string(ivan_dip.to_string()).to_string()
print(diploma_text)

# Проверка подписи
is_valid = ivan_dip.verify(key_manager.public_key)
print(f"\n----------------------------------------\nПодпись {'валидна' if is_valid else 'недействительна'}")

# Получаем ключи из менеджера
public_pem = key_manager.get_public_pem()
private_pem = key_manager.get_private_pem()

print(f"\nОткрытый ключ:\n{public_pem}")
print(f"\nЗакрытый ключ:\n{private_pem}")