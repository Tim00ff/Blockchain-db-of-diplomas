from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..models import Block

@dataclass
class MiningTask:
    block: Block
    status: str = "pending"
    assigned_to: Optional[str] = None
    start_nonce: int = 0
    end_nonce: int = 0
    created_at: datetime = datetime.now()
    started_at: Optional[datetime] = None

    @property
    def nonce_range(self) -> tuple[int, int]:
        """Возвращает диапазон nonce для майнинга"""
        return (self.start_nonce, self.end_nonce)

    def is_expired(self, timeout_seconds: int) -> bool:
        """Проверяет, истекло ли время выполнения задачи"""
        if self.started_at is None:
            return False
        return (datetime.now() - self.started_at).total_seconds() > timeout_seconds

    def assign_to_miner(self, miner_id: str, nonce_range_size: int = 100000):
        """Назначает задачу майнеру с указанием диапазона"""
        self.assigned_to = miner_id
        self.start_nonce = self.block.nonce  # Текущее значение nonce из блока
        self.end_nonce = self.start_nonce + nonce_range_size
        self.started_at = datetime.now()
        self.status = "mining"