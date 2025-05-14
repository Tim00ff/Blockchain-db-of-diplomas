import bcrypt
import json
import os
from typing import Dict, Optional
from ..models import User


def load_users() -> Dict[str, User]:
    """Загрузка пользователей из файла"""
    users = []
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                users_data = json.load(f)
                users = [User(**data) for data in users_data]
    except Exception as e:
        print(f"Error loading users: {str(e)}")
    return {u.username: u for u in users}


def authenticate(username: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    users = load_users()
    user = users.get(username)

    if user and bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        return user
    return None