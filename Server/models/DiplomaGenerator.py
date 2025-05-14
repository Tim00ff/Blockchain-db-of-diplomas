import json
from .KeyManager import KeyManager
from typing import Dict, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64


class DiplomaGenerator:
    def __init__(self, data: Optional[Dict] = None):
        self.data = data or {}
        self._initialize_template()

    def _initialize_template(self):
        """Базовый шаблон данных диплома"""
        self.data.setdefault("institution", "[Название учебного заведения]")
        self.data.setdefault("full_name", "Иванов Иван Иванович")
        self.data.setdefault("program", "Общее среднее образование")
        self.data.setdefault("qualification", "Бакалавр")
        self.data.setdefault("specialty", "Компьютерные науки")
        self.data.setdefault("issue_date", "01.06.2024")
        self.data.setdefault("reg_number", "0000-XXXX")
        self.data.setdefault("rector_name", "Петров П.П.")
        self.data.setdefault("secretary_name", "Сидорова А.А.")
        self.data.setdefault("signature", "")  # Пустая подпись по умолчанию

    def create_signature(self, key_manager: KeyManager) -> None:
        """Создает подпись используя KeyManager"""
        content = self._generate_content()
        self.data["signature"] = self._generate_signature(content, key_manager.private_key)

    def _generate_content(self) -> str:
        """Генерирует содержимое для подписи (без самой подписи)"""
        return json.dumps({k: v for k, v in self.data.items() if k != "signature"},
                          ensure_ascii=False)

    def _generate_signature(self, content: str, private_key: rsa.RSAPrivateKey) -> str:
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(content.encode('utf-8'))
        digest = hasher.finalize()

        signature = private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def to_dict(self) -> Dict:
        """Возвращает данные в виде словаря"""
        return self.data.copy()

    def to_string(self) -> str:
        """Формирует документ в человекочитаемом формате"""
        content = f"""\
                    Республика Беларусь
                    Министерство образования
                
                    Учебное заведение: {self.data['institution']}
                    ФИО выпускника: {self.data['full_name']}
                    Программа обучения: «{self.data['program']}»
                    Присвоенная квалификация: {self.data['qualification']}
                    Специальность: «{self.data['specialty']}»
                
                    Дата выдачи: {self.data['issue_date']}
                    Регистрационный номер: {self.data['reg_number']}
                
                    Подписи:
                    Ректор/Декан: {self.data['rector_name']}
                    Секретарь: {self.data['secretary_name']}
                
                    Электронная подпись: {self.data['signature']}
                
                    ----------------------------------------
                    ВНИМАНИЕ: Это декоративный шаблон. Не имеет юридической силы."""
        return content

    def save_to_file(self, filename: str) -> None:
        """Сохраняет диплом в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.to_string())

    @classmethod
    def from_string(cls, data_str: str) -> 'DiplomaGenerator':
        """Парсит документ из текстового формата"""
        data = {
            "institution": "",
            "full_name": "",
            "program": "",
            "qualification": "",
            "specialty": "",
            "issue_date": "",
            "reg_number": "",
            "rector_name": "",
            "secretary_name": "",
            "signature": ""
        }

        lines = data_str.split('\n')
        for line in lines:
            if 'Учебное заведение:' in line:
                data['institution'] = line.split(': ')[1].strip()
            elif 'ФИО выпускника:' in line:
                data['full_name'] = line.split(': ')[1].strip()
            elif 'Программа обучения:' in line:
                data['program'] = line.split('«')[1].split('»')[0].strip()
            elif 'Присвоенная квалификация:' in line:
                data['qualification'] = line.split(': ')[1].strip()
            elif 'Специальность:' in line:
                data['specialty'] = line.split('«')[1].split('»')[0].strip()
            elif 'Дата выдачи:' in line:
                data['issue_date'] = line.split(': ')[1].strip()
            elif 'Регистрационный номер:' in line:
                data['reg_number'] = line.split(': ')[1].strip()
            elif 'Ректор/Декан:' in line:
                data['rector_name'] = line.split(': ')[1].strip()
            elif 'Секретарь:' in line:
                data['secretary_name'] = line.split(': ')[1].strip()
            elif 'Электронная подпись:' in line:
                data['signature'] = line.split(': ')[1].strip()

        return cls(data)

    @classmethod
    def from_file(cls, filename: str) -> 'DiplomaGenerator':
        """Создает диплом из файла"""
        with open(filename, 'r', encoding='utf-8') as f:
            return cls.from_string(f.read())

    def verify(self, public_key: rsa.RSAPublicKey) -> bool:
        """Проверяет подпись диплома"""
        try:
            content = self._generate_content()
            signature = base64.b64decode(self.data["signature"])

            hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
            hasher.update(content.encode('utf-8'))
            digest = hasher.finalize()

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

    @classmethod
    def verify_file(cls, filename: str, public_key: rsa.RSAPublicKey) -> bool:
        """Проверяет диплом из файла"""
        diploma = cls.from_file(filename)
        return diploma.verify(public_key)