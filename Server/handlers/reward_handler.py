import json
import os
from typing import Dict, Optional

class RewardHandler:
    def __init__(self, file_path: str = "rewards.json"):
        self.file_path = file_path
        self.rewards: Dict[str, int] = {}
        self.load_rewards()

    def load_rewards(self) -> None:
        """Загружает данные из файла. Создает файл, если его нет."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    self.rewards = json.load(f)
            else:
                self.rewards = {}
                self.save_rewards()  # Создаем файл при первом запуске
        except Exception as e:
            print(f"Error loading rewards: {str(e)}")
            self.rewards = {}

    def save_rewards(self) -> None:
        """Сохраняет данные в файл атомарно."""
        try:
            temp_path = self.file_path + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(self.rewards, f, indent=2)
            os.replace(temp_path, self.file_path)
        except Exception as e:
            print(f"Error saving rewards: {str(e)}")

    def add_reward(self, username: str, amount: int = 1) -> None:
        """Добавляет награды пользователю. Создает запись, если пользователя нет."""
        self.rewards[username] = self.rewards.get(username, 0) + amount
        self.save_rewards()

    def get_rewards(self, username: str) -> int:
        """Возвращает количество наград. 0 если пользователь не существует."""
        return self.rewards.get(username, 0)

    def reset_rewards(
        self,
        username: Optional[str] = None
    ) -> None:
        """Сбрасывает награды. Для всех, если username не указан."""
        if username:
            if username in self.rewards:
                del self.rewards[username]
        else:
            self.rewards = {}
        self.save_rewards()

    def __str__(self) -> str:
        return json.dumps(self.rewards, indent=2)