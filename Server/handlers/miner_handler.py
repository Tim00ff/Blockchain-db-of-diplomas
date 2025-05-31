from threading import Lock
from typing import List
from ..models import MiningTask, Blockchain, Block
from ..utils import response_formatter
from datetime import datetime
from .reward_handler import RewardHandler
def handle_mine_command(
        miner_id: str,
        queue: List[MiningTask],
        lock: Lock,
        nonce_range_size: int = 400000
) -> str:
    """Выдача задания майнеру"""
    with lock:
        if not queue:
            return response_formatter.format_error("No tasks available", 401)

        task = next((t for t in queue if (t.status == 'pending' or 'mining')), None)
        if not task:
            return response_formatter.format_error("No pending tasks", 401)

        task.assign_to_miner(miner_id, nonce_range_size)
        return response_formatter.task_data(task, miner_id)


def handle_solution(
        command: str,
        miner_id: str,
        blockchain: Blockchain,
        task_queue: List[MiningTask],
        rewards : RewardHandler,
        lock: Lock
) -> str:
    """Обработка решения майнера с обновлением следующих задач в очереди"""
    try:
        # Парсинг команды: SUBMIT_SOLUTION <nonce> <hash>
        _, nonce_str, submitted_hash = command.split()
        nonce = int(nonce_str)
    except ValueError:
        return response_formatter.format_error("Invalid format: SUBMIT_SOLUTION <nonce> <hash>")

    with lock:
        if not task_queue:
            return response_formatter.format_error("No active tasks")

        # Берем первую задачу из очереди (FIFO)
        task = task_queue[0]
        block = task.block
        block.nonce = nonce
        start, stop = task.get_miner_range(miner_id)

        # Проверка решения
        calculated_hash = block.calculate_hash()
        if not nonce in range(start, stop):
            return response_formatter.format_error("Nonce is outside of range")
        if calculated_hash != submitted_hash:
            return response_formatter.format_error("Invalid hash")

        if not calculated_hash.startswith('0' * block.difficulty):
            return response_formatter.format_error("Difficulty not satisfied")


        # Добавляем в блокчейн
        blockchain.add_block(block)

        # Обновляем последующие задачи в очереди
        if len(task_queue) > 0:
            # Удаляем завершенную задачу
            task_queue.pop(0)

            # Обновляем
            if len(task_queue) > 0:
                task_queue[0].block.prev_hash = block.hash
                task_queue[0].block.id = blockchain.current_id


            # Начисляем награду
            rewards.add_reward(miner_id, 1)

            return response_formatter.format_response(
                "204 Block mined",
                data={
                    "block_id": block.id,
                    "prev_hash": block.prev_hash,
                    "new_hash": block.hash,
                    "reward": rewards[miner_id]
                }
            )