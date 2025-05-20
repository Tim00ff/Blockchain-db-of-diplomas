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
        block_id = 0
        prev_hash = "0" * 64
        if len(queue) == 0:
            # Если очередь пуста - берем актуальные данные из блокчейна
            block_id = blockchain.current_id
            prev_hash = (
                blockchain.chain[-1].hash
                if blockchain.chain
                else "0" * 64
            )

        # Создание временного блока для проверки
        new_block = Block(
            block_id=block_id,  # Temporary ID
            diploma_data={**diploma_data, "signature": signature},
            public_key=public_key,
            prev_hash=prev_hash  # Dummy value for verification
        )
        if not new_block.verify_diploma():
            return response_formatter.format_error("Invalid diploma signature")

        new_block.difficulty = blockchain.difficulty
        new_block.hash = new_block.calculate_hash()

        # Добавление в очередь майнинга
        with lock:
            queue.append(MiningTask(new_block, blockchain, "pending"))
            return response_formatter.format_response(
                "202 Block queued for mining",
                data={
                    "block_id": block_id if len(queue) == 1 else 0,
                    "initial_hash": new_block.hash,
                    "difficulty": new_block.difficulty,
                    "queue_status": "pending" if len(queue) == 1 else "pending"
                }
            )

    except Exception as e:
        return response_formatter.format_error(f"Error processing block: {str(e)}")