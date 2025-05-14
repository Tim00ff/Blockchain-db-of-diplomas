import json
from hashlib import sha256
from time import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import os
from DiplomaGenerator import DiplomaGenerator


class Block:
    def __init__(self, block_id: int, diploma_data: dict, public_key: rsa.RSAPublicKey, prev_hash: str = None):
        self.id = block_id
        self.prev_hash = prev_hash
        self.timestamp = time()
        self.diploma_data = diploma_data
        self.public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        self.signature = diploma_data['signature']
        self.nonce = 0
        self.difficulty = 4
        self.hash = self.calculate_hash()

        self._validate_diploma(public_key)

    def _validate_diploma(self, public_key: rsa.RSAPublicKey):
        """Проверка валидности подписи диплома"""
        temp_diploma = DiplomaGenerator(self.diploma_data.copy())
        if not temp_diploma.verify(public_key):
            raise ValueError("Invalid diploma signature!")

    def verify_diploma(self) -> bool:
        """Проверяет подпись диплома"""
        try:
            public_key = serialization.load_pem_public_key(
                self.public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            return DiplomaGenerator(self.diploma_data.copy()).verify(public_key)
        except Exception:
            return False

    def calculate_hash(self) -> str:
        data_string = (
                str(self.prev_hash) +
                str(self.timestamp) +
                json.dumps(self.diploma_data, sort_keys=True) +
                self.public_key_pem +
                self.signature +
                str(self.nonce) +
                str(self.difficulty))
        return sha256(data_string.encode('utf-8')).hexdigest()

    def mine(self) -> None:
        while self.hash[:self.difficulty] != '0' * self.difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def save_to_file(self, folder: str) -> None:
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"Block_{self.id:05d}.json")
        data = {
            "id": self.id,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "diploma_data": self.diploma_data,
            "public_key": self.public_key_pem,
            "signature": self.signature,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "hash": self.hash
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def from_file(cls, filename: str) -> 'Block':
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        public_key = serialization.load_pem_public_key(
            data['public_key'].encode('utf-8'),
            backend=default_backend()
        )

        block = cls(
            block_id=data['id'],
            diploma_data=data['diploma_data'],
            public_key=public_key,
            prev_hash=data['prev_hash']
        )

        block.timestamp = data['timestamp']
        block.nonce = data['nonce']
        block.difficulty = data['difficulty']
        block.hash = data['hash']

        return block

    def __repr__(self) -> str:
        return f"Block(id={self.id}, hash={self.hash[:10]}...)"