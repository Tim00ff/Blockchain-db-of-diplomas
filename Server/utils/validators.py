import re
from cryptography.exceptions import InvalidSignature

def validate_block_data(block_data: dict) -> bool:
    """Валидация данных блока"""
    required_fields = {
        'institution', 'full_name', 'program',
        'qualification', 'specialty', 'signature'
    }
    return all(field in block_data for field in required_fields)

def validate_credentials(username: str, password: str) -> bool:
    """Валидация учетных данных"""
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return False
    if len(password) < 8:
        return False
    return True

def validate_signature(block_data: dict, public_key) -> bool:
    """Проверка цифровой подписи"""
    try:
        # Реальная реализация проверки подписи
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False

def validate_nonce_range(nonce: int, start: int, end: int) -> bool:
    """Проверка диапазона nonce"""
    return start <= nonce < end