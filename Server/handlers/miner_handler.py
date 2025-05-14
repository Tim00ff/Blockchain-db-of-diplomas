from threading import Lock
from typing import List
from ..models.task import MiningTask
from ..utils import response_formatter


def handle_mine_command(
        miner_id: str,
        queue: List[MiningTask],
        lock: Lock,
        nonce_range_size: int = 100000
) -> str:
    """Выдача задания майнеру"""
    with lock:
        if not queue:
            return response_formatter.format_error("No tasks available")

        task = next((t for t in queue if t.status == 'pending'), None)
        if not task:
            return response_formatter.format_error("No pending tasks")

        task.assign_to(miner_id, nonce_range_size)
        return response_formatter.task_data(task)