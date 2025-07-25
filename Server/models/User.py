from dataclasses import dataclass

@dataclass
class User:
    username: str
    hashed_password: str
    role: str
    status: str = "active"

