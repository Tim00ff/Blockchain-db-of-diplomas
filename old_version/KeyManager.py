from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import os


class KeyManager:
    def __init__(self, generate: bool = True):
        self._private_key: RSAPrivateKey = None
        self._public_key: RSAPublicKey = None

        if generate:
            self._generate_keys()

    def _generate_keys(self) -> None:
        """Генерирует новую пару RSA ключей"""
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self._public_key = self._private_key.public_key()

    @property
    def public_key(self) -> RSAPublicKey:
        """Возвращает объект публичного ключа"""
        return self._public_key

    @property
    def private_key(self) -> RSAPrivateKey:
        """Возвращает объект приватного ключа"""
        return self._private_key

    def get_public_pem(self) -> str:
        """Возвращает публичный ключ в PEM-формате"""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def get_private_pem(self) -> str:
        """Возвращает приватный ключ в PEM-формате"""
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

    def save_to_file(self, filename: str) -> None:
        """
        Сохраняет ключи в файл
        Формат:
        -----BEGIN PUBLIC KEY-----
        ...
        -----END PUBLIC KEY-----
        === KEY MANAGER DELIMITER ===
        -----BEGIN PRIVATE KEY-----
        ...
        -----END PRIVATE KEY-----
        """
        public_pem = self.get_public_pem()
        private_pem = self.get_private_pem()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{public_pem}\n=== KEY MANAGER DELIMITER ===\n{private_pem}")

    @classmethod
    def from_file(cls, filename: str) -> 'KeyManager':
        """Загружает ключи из файла"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Key file {filename} not found")

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            public_pem, private_pem = content.split("=== KEY MANAGER DELIMITER ===")
        except ValueError:
            raise ValueError("Invalid key file format") from None

        km = cls(generate=False)
        km._public_key = serialization.load_pem_public_key(
            public_pem.strip().encode('utf-8'),
            backend=default_backend()
        )
        km._private_key = serialization.load_pem_private_key(
            private_pem.strip().encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        return km

    @classmethod
    def from_pem(cls, public_pem: str, private_pem: str) -> 'KeyManager':
        """Создает экземпляр из PEM-строк"""
        km = cls(generate=False)
        km._public_key = serialization.load_pem_public_key(
            public_pem.encode('utf-8'),
            backend=default_backend()
        )
        km._private_key = serialization.load_pem_private_key(
            private_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        return km

    def __eq__(self, other: 'KeyManager') -> bool:
        """Проверяет эквивалентность ключей"""
        return (
                self.get_public_pem() == other.get_public_pem() and
                self.get_private_pem() == other.get_private_pem()
        )