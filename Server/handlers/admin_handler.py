import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from threading import Lock
from typing import List
from ..utils import response_formatter
from ..models import MiningTask
from ..models import Block


def handle_add_block(command: str, queue: List[MiningTask], lock: Lock, blockchain) -> str:
    """Обработка добавления нового блока администратором"""
    try:
        # Парсинг команды
        _, block_json = command.split(' ', 1)
        incoming_data = json.loads(block_json)

        # Извлечение данных
        diploma_data = incoming_data['diploma_data']
        public_key_pem = incoming_data['public_key']
        signature = incoming_data['signature']

        # Конвертация PEM в RSAPublicKey
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )

        # Создание временного блока для проверки
        temp_block = Block(
            block_id=0,
            diploma_data={**diploma_data, "signature": signature},
            public_key=public_key,
            prev_hash="0" * 64
        )

        if not temp_block.verify_diploma():
            return response_formatter.format_error("Invalid diploma signature")

        # Создание реального блока
        block_id = len(blockchain.chain)
        prev_hash = blockchain.last_block.hash if blockchain.chain else "0" * 64

        new_block = Block(
            block_id=block_id,
            diploma_data={**diploma_data, "signature": signature},
            public_key=public_key,
            prev_hash=prev_hash
        )

        # Установка временных значений
        new_block.nonce = 0
        new_block.hash = new_block.calculate_hash()
        new_block.difficulty = blockchain.difficulty

        # Добавление в очередь майнинга
        with lock:
            queue.append(MiningTask(new_block))
            return response_formatter.format_response(
                "Block queued for mining",
                data={
                    "block_id": block_id,
                    "initial_hash": new_block.hash,
                    "difficulty": new_block.difficulty
                }
            )

    except Exception as e:
        return response_formatter.format_error(f"Error processing block: {str(e)}")