import json


def format_response(command: str, data: dict, status: str = "OK") -> str:
    """Форматирование успешного ответа"""
    return status + " " + command + "\r\n" + json.dumps({"data": data}) + "\r\n\r\n"


def format_error(error_msg: str, error_code: int = 400) -> str:
    """Форматирование сообщения об ошибке"""
    return "ERROR " + str(error_code) + "\r\n" + error_msg + "\r\n\r\n"

def format_success(success_msg: str, success_code: int = 200) -> str:
    """Форматирование сообщения об успехе"""
    return "OK " + str(success_code) + "\r\n" + success_msg + "\r\n\r\n"

def task_data(task, username: str) -> str:
    """Форматирование данных майнинг-задачи"""
    task_info = {
        "block_id": task.block.id,
        "nonce_start": task.assigned_miners[username][0],
        "nonce_end": task.assigned_miners[username][1],
        "info": task.block.hash_info(),
        "difficulty": task.block.difficulty
    }
    # Validate JSON serialization
    try:
        json.dumps(task_info["info"])  # Test escaping
    except TypeError:
        task_info["info"] = "Invalid data"
    return format_response("MINING_TASK", task_info)

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