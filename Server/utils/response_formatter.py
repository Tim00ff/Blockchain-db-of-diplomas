import json


def format_response(command: str, data: dict, status: str = "OK") -> str:
    """Форматирование успешного ответа"""
    return status + " " + command + "\r\n" + json.dumps({"data": data}) + "\r\n\r\n"


def format_error(error_msg: str, error_code: int = 400) -> str:
    """Форматирование сообщения об ошибке"""
    return "ERROR " + str(error_code) + "\r\n" + error_msg + "\r\n\r\n"

def format_success(success_msg: str, success_code: int = 200) -> str:
    """Форматирование сообщения об успехе"""
    return "ERROR " + str(success_code) + "\r\n" + success_msg + "\r\n\r\n"

def format_help(authenticated: bool, role: str = None) -> str:
    """Форматирование справочного сообщения"""
    help_msg = {
        "basic": [
            "VIEW_BLOCK <id> - View block by ID",
            "HELP - Show this message"
        ],
        "admin": [
            "ADD_BLOCK <json_data> - Add new block to queue",
            "LIST_QUEUE - Show pending blocks"
        ],
        "miner": [
            "MINE - Get mining task",
            "SUBMIT_SOLUTION <hash> - Submit block solution"
        ]
    }

    response = help_msg["basic"]
    if authenticated and role:
        response += help_msg.get(role.lower(), [])
    output = ""
    for value in response:
        output += value + "\r\n"
    return "HELP\r\n" + output