import threading
from typing import List, Tuple, Optional
from ..handlers import (
    auth_handler,
    admin_handler,
    miner_handler,
    view_handler,
    RewardHandler
)
from ..utils import response_formatter
from ..models import User, MiningTask, Blockchain

class RequestRouter:
    def __init__(
            self,
            blockchain: Blockchain,
            task_queue: List[MiningTask],
            rewards: RewardHandler,
            lock: threading.Lock
    ):
        self.blockchain = blockchain
        self.task_queue = task_queue
        self.rewards = rewards
        self.lock = lock
        self.miner_counter = 0
        self.miner_lock = threading.Lock()

    def _parse_request(self, raw_data: str) -> Tuple[List[str], Optional[User]]:
        """Парсинг сырых данных запроса"""
        try:
            lines = [line.strip() for line in raw_data.split('\r\n') if line.strip()]
            if not lines:
                return [], None

            # Выделение команды LOGIN если есть
            login_index = next(
                (i for i, line in enumerate(lines) if line.startswith("LOGIN")),
                None
            )

            if login_index is not None:
                # Аутентификация пользователя
                _, username, password = lines[login_index].split()
                user = auth_handler.authenticate(username, password)
                return lines[login_index + 1:], user

            return lines, None

        except Exception as e:
            return [], None

    def _handle_unauthorized(self, command: str) -> str:
        """Обработка команд для неавторизованных пользователей"""
        if command == "HELP":
            return response_formatter.format_help(authenticated=False)

        if command.startswith("VIEW_BLOCK"):
            try:
                _, block_id = command.split()
                return view_handler.handle_view_block(self.blockchain, block_id)
            except:
                return response_formatter.format_error("Invalid block ID")

        return response_formatter.format_error("Authentication required")

    def _handle_authorized(self, commands: List[str], user: User) -> str:
        """Обработка команд для авторизованных пользователей"""
        responses = []

        for command in commands:
            if command == "HELP":
                responses.append(response_formatter.format_help(
                    authenticated=True,
                    role=user.role
                ))
                continue

            try:
                if user.role == "admin":
                    response = self._handle_admin_command(command, user.username)
                elif user.role == "miner":
                    response = self._handle_miner_command(command, user.username)
                else:
                    response = response_formatter.format_error("Unauthorized role")

            except Exception as e:
                response = response_formatter.format_error(f"Processing error: {str(e)}")

            responses.append(response)

        return '\r\n'.join(responses)

    def _handle_admin_command(self, command: str, username: str) -> str:
        """Обработка команд администратора"""
        if command.startswith("ADD_BLOCK"):
            return admin_handler.handle_add_block(
                command=command,
                queue=self.task_queue,
                lock=self.lock,
                blockchain=self.blockchain
            )

        if command == "LIST_QUEUE":
            with self.lock:
                return response_formatter.format_success(
                    f"Pending tasks: {len(self.task_queue)}"
                )

        return response_formatter.format_error("Unknown admin command")

    def _handle_miner_command(self, command: str, username: str) -> str:
        """Обработка команд майнера"""
        if command == "MINE":
            return miner_handler.handle_mine_command(
                username,
                self.task_queue,
                self.lock
            )

        if command.startswith("SUBMIT_SOLUTION"):
            return miner_handler.handle_solution(
                command,
                username,
                self.blockchain,
                self.task_queue,
                self.rewards,
                self.lock
            )

        return response_formatter.format_error("Unknown miner command")

    def route_request(self, raw_data: str) -> str:
        """Основной метод маршрутизации запросов"""
        try:
            commands, user = self._parse_request(raw_data)

            if not commands:
                if not user:
                    return response_formatter.format_error("Empty request")
                if user:
                    return response_formatter.format_success("PASS", 201)

            # Обработка неавторизованных команд
            if user is None:
                return self._handle_unauthorized(commands[0])

            # Обработка авторизованных команд
            response = self._handle_authorized(commands, user)
            return response + "\r\n\r\n"

        except Exception as e:
            return response_formatter.format_error(f"Server error: {str(e)}") + "\r\n\r\n"