# ServerInteract.py
import json
import bcrypt
import os
from threading import Lock
from Blockchain import Blockchain
from Block import Block
from KeyManager import KeyManager
from DiplomaGenerator import DiplomaGenerator
import time

def load_users():
    """Load users from JSON file with role support"""
    users = []
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                users = json.load(f)
    except Exception as e:
        print(f"Error loading users: {str(e)}")
    return {u['username']: u for u in users}


def verify_credentials(username, password):
    """Verify user credentials and return role"""
    users = load_users()
    user = users.get(username)
    if not user:
        return None

    if bcrypt.checkpw(password.encode(), user['hashed_password'].encode()):
        return user['role']
    return None


def process_client_request(raw_data, blockchain, block_queue, rewards_dict, lock):
    try:
        response = []
        lines = [line.strip() for line in raw_data.split('\r\n') if line.strip()]
        if not lines:
            return "EMPTY_REQUEST\r\n\r\n"

        # Обработка HELP для неавторизованных пользователей
        if lines[0] == "HELP":
            return get_help_message(authenticated=False) + "\r\n\r\n"
        elif lines[0].startswith("VIEW_BLOCK"):
            response.append(handle_view_block(lines[0], blockchain))
        if not lines[0].startswith("LOGIN"):
            return "" if not response else "/r/n".join(response) + "\r\nAUTH_REQUIRED Use HELP for commands\r\n\r\n"
        auth_result = handle_auth(lines[0])
        if not auth_result['success']:
            return auth_result['response'] + "\r\n\r\n"

        role = auth_result['role']
        print(role)
        username = auth_result['username']

        # Обработка оставшихся команд после LOGIN
        for line in lines[1:]:
            if line == "HELP":
                response.append(get_help_message(authenticated=True,role=role))
            elif line.startswith("VIEW_BLOCK"):
                response.append(handle_view_block(line, blockchain))
            elif role == "admin" and line.startswith("ADD_BLOCK"):
                response.append(handle_admin_command(line, block_queue, lock))
            elif role == "miner" and line.startswith("MINE"):
                response.append(handle_miner_command(
                    line,
                    username,
                    blockchain,
                    block_queue,
                    rewards_dict,
                    lock
                ))
            else:
                response.append("UNKNOWN_COMMAND")

        return "\r\n".join(response) + "\r\n\r\n"

    except Exception as e:
        return f"ERROR: {str(e)}\r\n\r\n"


def get_help_message(authenticated=False, role=None):
    base_help = """\
                    \rAVAILABLE COMMANDS:
                    \rVIEW_BLOCK <id> - View block by ID
                    \rHELP - Show this message
                \r"""

    if authenticated:
        role_help = {
            "admin": """\
                        \rADMIN COMMANDS:
                        \rLOGIN <user> <pass> - Authenticate
                        \rADD_BLOCK <json_data> - Add new block to queue
                    \r""",
            "miner": """\
                        \rMINER COMMANDS:
                        \rLOGIN <user> <pass> - Authenticate
                        \rMINE - Get mining task
                        \rSOLVE_BLOCK <hash> - Submit block solution
                    \r"""
        }
        return base_help + role_help.get(role, "")

    return base_help + "LOGIN <user> <pass> - Authenticate for more commands"

def handle_view_block(command, blockchain):
    """Handle block viewing for visitors"""
    try:
        _, block_id = command.split()
        block = blockchain.get_block(int(block_id))
        return f"BLOCK_DATA {json.dumps(block.diploma_data)}\r\n\r\n"
    except (ValueError, IndexError):
        return "INVALID_BLOCK_ID\r\n\r\n"
    except AttributeError:
        return "BLOCK_NOT_FOUND\r\n\r\n"


def handle_auth(login_cmd):
    """Handle authentication"""
    try:
        _, username, password = login_cmd.split()
        role = verify_credentials(username, password)
        if not role:
            return {'success': False, 'response': "AUTH_FAILED\r\n\r\n"}

        return {
            'success': True,
            'role': role,
            'username': username,
            'response': f"AUTH_SUCCESS {role.upper()}\r\n"
        }
    except ValueError:
        return {'success': False, 'response': "INVALID_LOGIN_FORMAT\r\n\r\n"}


def handle_admin_commands(lines, username, block_queue, lock):
    """Process admin commands"""
    if len(lines) < 2:
        return "INCOMPLETE_COMMAND\r\n\r\n"

    command = lines[1]
    if command.startswith("ADD_BLOCK"):
        return add_block_to_queue(command, username, block_queue, lock)

    return "UNKNOWN_ADMIN_COMMAND\r\n\r\n"


def add_block_to_queue(command, username, block_queue, lock):
    """Add signed block to mining queue"""
    try:
        _, block_json = command.split(' ', 1)
        block_data = json.loads(block_json)

        # Verify admin signature
        diploma = DiplomaGenerator(block_data)
        if not diploma.verify(KeyManager.from_file(f"keys/{username}_pub.pem").public_key):
            return "INVALID_BLOCK_SIGNATURE\r\n\r\n"

        with lock:
            block_queue.append({
                'data': block_data,
                'added_by': username,
                'status': 'pending'
            })

        return "BLOCK_ADDED_TO_QUEUE\r\n\r\n"
    except json.JSONDecodeError:
        return "INVALID_BLOCK_DATA\r\n\r\n"
    except Exception as e:
        return f"BLOCK_ERROR: {str(e)}\r\n\r\n"


def handle_miner_commands(lines, username, blockchain, block_queue, rewards, lock):
    """Process miner commands"""
    if len(lines) < 2:
        return "INCOMPLETE_COMMAND\r\n\r\n"

    command = lines[1]
    if command == "GET_TASK":
        return assign_mining_task(username, block_queue, blockchain, lock)
    elif command.startswith("SUBMIT_SOLUTION"):
        return process_solution(command, username, blockchain, block_queue, rewards, lock)

    return "UNKNOWN_MINER_COMMAND\r\n\r\n"


def assign_mining_task(username, block_queue, blockchain, lock):
    """Assign mining task to miner"""
    with lock:
        if not block_queue:
            return "NO_PENDING_TASKS\r\n\r\n"

        task = block_queue[0]
        if task['status'] != 'pending':
            return "NO_PENDING_TASKS\r\n\r\n"

        task['status'] = 'mining'
        task['miner'] = username
        return f"MINING_TASK {json.dumps(task['data'])}\r\n\r\n"


def process_solution(command, username, blockchain, block_queue, rewards, lock):
    """Process miner's solution"""
    try:
        _, block_hash = command.split()

        with lock:
            if not block_queue:
                return "INVALID_TASK\r\n\r\n"

            task = block_queue[0]
            if task['status'] != 'mining' or task['miner'] != username:
                return "SOLUTION_REJECTED\r\n\r\n"

            # Verify hash meets difficulty
            if not block_hash.startswith('0' * blockchain.chain[0].difficulty):
                return "INVALID_SOLUTION\r\n\r\n"

            # Add to blockchain
            new_block = Block(
                block_id=len(blockchain),
                diploma_data=task['data'],
                public_key=KeyManager.from_file(f"keys/{task['added_by']}_pub.pem").public_key,
                prev_hash=blockchain.chain[-1].hash if blockchain.chain else "0" * 64
            )
            new_block.hash = block_hash
            blockchain.add_block(new_block)

            # Update rewards
            rewards[username] = rewards.get(username, 0) + 1
            block_queue.pop(0)

            return f"SOLUTION_ACCEPTED {rewards[username]}\r\n\r\n"

    except Exception as e:
        return f"SOLUTION_ERROR: {str(e)}\r\n\r\n"


def handle_admin_command(command: str, block_queue: list, lock: Lock) -> str:
    """Обработка команд администратора"""
    try:
        if command.startswith("ADD_BLOCK"):
            _, block_json = command.split(' ', 1)
            block_data = json.loads(block_json)

            # Проверка подписи
            if not verify_admin_signature(block_data):
                return "INVALID_SIGNATURE"

            with lock:
                block_queue.append({
                    'data': block_data,
                    'status': 'pending',
                    'timestamp': time.time()
                })
            return "BLOCK_ADDED_TO_QUEUE"

        elif command == "LIST_QUEUE":
            with lock:
                return f"QUEUE_LENGTH {len(block_queue)}"

        return "UNKNOWN_ADMIN_COMMAND"

    except json.JSONDecodeError:
        return "INVALID_JSON"
    except Exception as e:
        return f"ADMIN_ERROR: {str(e)}"


def handle_miner_command(command: str,
                         username: str,
                         blockchain: Blockchain,
                         block_queue: list,
                         rewards: dict,
                         lock: Lock) -> str:
    """Обработка команд майнера"""
    try:
        if command == "MINE":
            with lock:
                if not block_queue:
                    return "NO_BLOCKS_TO_MINE"

                block = block_queue[0]
                if block['status'] != 'pending':
                    return "NO_AVAILABLE_BLOCKS"

                block['status'] = 'mining'
                block['miner'] = username
                return f"MINING_TASK {json.dumps(block['data'])}"

        elif command.startswith("SUBMIT"):
            _, block_hash = command.split(' ')
            with lock:
                if not block_queue:
                    return "INVALID_SUBMISSION"

                block = block_queue[0]
                if block['status'] != 'mining' or block['miner'] != username:
                    return "SUBMISSION_REJECTED"

                # Проверка хэша
                if validate_block_hash(block['data'], block_hash):
                    # Добавление в блокчейн
                    new_block = Block(
                        block_id=len(blockchain),
                        diploma_data=block['data'],
                        public_key=load_public_key(block['data']['admin']),
                        prev_hash=blockchain.chain[-1].hash if blockchain.chain else '0' * 64
                    )
                    blockchain.add_block(new_block)

                    # Начисление награды
                    rewards[username] = rewards.get(username, 0) + 1
                    block_queue.pop(0)
                    return f"SUBMISSION_ACCEPTED Reward: {rewards[username]}"

                return "INVALID_HASH"

        return "UNKNOWN_MINER_COMMAND"

    except Exception as e:
        return f"MINER_ERROR: {str(e)}"


# Вспомогательные функции
def verify_admin_signature(block_data: dict) -> bool:
    """Проверка подписи администратора"""
    try:
        diploma = DiplomaGenerator(block_data)
        public_key = KeyManager.from_file(f"keys/{block_data['admin']}_pub.pem").public_key
        return diploma.verify(public_key)
    except:
        return False


def validate_block_hash(block_data: dict, submitted_hash: str) -> bool:
    """Проверка соответствия хэша"""
    temp_block = Block(
        block_id=0,
        diploma_data=block_data,
        public_key=load_public_key(block_data['admin']),
        prev_hash=""
    )
    return temp_block.calculate_hash().startswith('0' * temp_block.difficulty)


def load_public_key(admin_name: str):
    """Загрузка публичного ключа администратора"""
    return KeyManager.from_file(f"keys/{admin_name}_pub.pem").public_key