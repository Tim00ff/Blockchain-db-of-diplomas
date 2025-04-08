from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64


class DiplomaGenerator:
    def __init__(self, data: dict):
        self.data = data
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

        # Шаблон без электронной подписи
        self.template = """\
                        Республика Беларусь
                        Министерство образования
                        {institution}
                        (Герб/Печать здесь)
                        
                        ДИПЛОМ
                        
                        Настоящим удостоверяется, что
                        {full_name}
                        успешно завершил(а) программу
                        «{program}»
                        и присваивается квалификация
                        {qualification}
                        по специальности
                        «{specialty}»
                        
                        Дата выдачи: {issue_date}
                        Регистрационный номер: {reg_number}
                        
                        Подписи:
                        Ректор/Декан: {rector_name}
                        Секретарь: {secretary_name}
                        """

    def _generate_base_content(self) -> str:
        """Генерирует основное содержание диплома без подписи"""
        return self.template.format(
            institution=self.data.get('institution', '[Название учебного заведения]'),
            full_name=self.data.get('full_name', 'Иванов Иван Иванович'),
            program=self.data.get('program', 'Общее среднее образование'),
            qualification=self.data.get('qualification', 'Бакалавр'),
            specialty=self.data.get('specialty', 'Компьютерные науки'),
            issue_date=self.data.get('issue_date', '01.06.2024'),
            reg_number=self.data.get('reg_number', '0000-XXXX'),
            rector_name=self.data.get('rector_name', 'Петров П.П.'),
            secretary_name=self.data.get('secretary_name', 'Сидорова А.А.')
        )

    def generate(self) -> str:
        """Генерирует полный диплом с электронной подписью"""
        content = self._generate_base_content()
        signature = self._create_signature(content)
        return f"{content}\n\nЭЛЕКТРОННАЯ ПОДПИСЬ: {signature}\n\n" \
               "----------------------------------------\n" \
               "ВНИМАНИЕ: Это декоративный шаблон. Не имеет юридической силы."

    def _create_signature(self, content: str) -> str:
        """Создает электронную подпись для контента"""
        # Хэшируем содержание
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(content.encode('utf-8'))
        digest = hasher.finalize()

        # Создаем подпись
        signature = self.private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode('utf-8')

    def get_public_key(self) -> bytes:
        """Возвращает публичный ключ в PEM формате"""
        return self.public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )

    def get_public_key_pem(self) -> str:
        """Serialize public key to PEM string"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def get_private_key_pem(self) -> str:
        """Serialize private key to PEM string (use with caution!)"""
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

    @staticmethod
    def verify_diploma(diploma_text: str, public_key_pem: bytes) -> bool:
        """Проверяет валидность электронной подписи"""
        try:
            # Извлекаем основные данные и подпись
            parts = diploma_text.split("\n\nЭЛЕКТРОННАЯ ПОДПИСЬ: ")
            if len(parts) != 2:
                return False

            content, signature_part = parts
            signature = base64.b64decode(signature_part.split("\n")[0])

            # Хэшируем содержание
            hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
            hasher.update(content.encode('utf-8'))
            digest = hasher.finalize()

            # Загружаем публичный ключ
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )

            # Проверяем подпись
            public_key.verify(
                signature,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True

        except Exception as e:
            print(f"Ошибка верификации: {str(e)}")
            return False
#
#
# # Пример использования
# if __name__ == "__main__":
#     data = {
#         'institution': 'Государственный университет информатики',
#         'full_name': 'Смирнова Анна Дмитриевна',
#         'program': 'Высшее образование по специальности "Программная инженерия"',
#         'qualification': 'Магистр',
#         'specialty': 'Информационные системы и технологии',
#         'issue_date': '15.07.2024',
#         'reg_number': '2024-BY-5678',
#         'rector_name': 'Иванов И.И.',
#         'secretary_name': 'Петрова М.С.'
#     }
#
#     # Генерация диплома
#     generator = DiplomaGenerator(data)
#     diploma = generator.generate()
#     print(diploma)
#
#     # Проверка подписи
#     public_key_pem = generator.get_public_key()
#     is_valid = DiplomaGenerator.verify_diploma(diploma, public_key_pem)
#     print(f"Подпись {'валидна' if is_valid else 'недействительна'}")
#
#     # Проверка с измененным содержимым (должна быть невалидна)
#     tampered_diploma = diploma.replace("Магистр", "Доктор наук")
#     is_valid_tampered = DiplomaGenerator.verify_diploma(tampered_diploma, public_key_pem)
#     print(f"Подпись измененного документа {'валидна' if is_valid_tampered else 'недействительна'}")
