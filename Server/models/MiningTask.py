from datetime import datetime
from typing import Optional, Dict, Tuple, Any
from ..models import Block
import threading

class MiningTask:
    def __init__(
            self,
            block: Block,
            blockchain: Any,
            status: str = "pending",
            assigned_miners: Dict[str, Tuple[int, int]] = None,
            created_at: Optional[datetime] = None,
            started_at: Optional[datetime] = None,
            base_nonce: int = 0
    ):
        """
        Initialize a MiningTask with support for multiple miners.

        :param block: Block to be mined
        :param blockchain: Reference to blockchain for chain state access
        :param status: Current status of the mining task
        :param assigned_miners: Dictionary of miner usernames and their nonce ranges
        :param created_at: Timestamp when task was created
        :param started_at: Timestamp when mining started
        :param base_nonce: Starting point for nonce range allocation
        """
        self.block = block
        self.blockchain = blockchain
        self.status = status
        self.assigned_miners = assigned_miners or {}
        self.created_at = created_at or datetime.now()
        self.started_at = started_at
        self.base_nonce = base_nonce
        self.lock = threading.Lock()  # For thread-safe operations

    @property
    def current_max_nonce(self) -> int:
        """Get the highest allocated nonce value"""
        if not self.assigned_miners:
            return self.base_nonce
        return max(end for (start, end) in self.assigned_miners.values())

    def get_next_nonce_range(self, range_size: int = 10000) -> Tuple[int, int]:
        """Calculate next available nonce range"""
        next_start = self.current_max_nonce + 1
        return next_start, next_start + range_size - 1

    def assign_to_miner(self, miner_id: str, range_size: int = 10000) -> bool:
        """Assign a new nonce range to a miner"""
        with self.lock:
            if miner_id in self.assigned_miners:
                return False  # Miner already has a range

            new_range = self.get_next_nonce_range(range_size)
            self.assigned_miners[miner_id] = new_range
            print(self.assigned_miners)
            # Update task status if first assignment
            if self.status == "pending":
                self.status = "mining"
                self.started_at = datetime.now()

            return True

    def get_miner_range(self, miner_id: str) -> Optional[Tuple[int, int]]:
        """Get assigned range for a specific miner"""
        return self.assigned_miners.get(miner_id)

    def is_fully_assigned(self, total_range: int = 2 ** 32) -> bool:
        """Check if all possible nonce values are assigned"""
        return self.current_max_nonce >= total_range - 1

    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if the task has exceeded processing time"""
        if self.started_at is None:
            return False
        return (datetime.now() - self.started_at).total_seconds() > timeout_seconds

    def reset_expired_ranges(self, timeout_seconds: int):
        """Reset ranges that haven't been completed in time"""
        with self.lock:
            expired_miners = [
                miner_id for miner_id, (start, end) in self.assigned_miners.items()
                if (datetime.now() - self.started_at).total_seconds() > timeout_seconds
            ]
            for miner_id in expired_miners:
                del self.assigned_miners[miner_id]

    def __repr__(self) -> str:
        """Debug-friendly representation"""
        return (
            f"status={self.status} miners={len(self.assigned_miners)} "
            f"current_max_nonce={self.current_max_nonce}>"
        )