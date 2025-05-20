import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread
from time import sleep
from time import time as current_time
from Miner_Client import MinerClient
class MinerGUI:
    def __init__(self, root):
        self.root = root
        self.client = None
        self.mining_thread = None

        root.title("Blockchain Miner")
        root.geometry("800x600")
        self.create_widgets()
        self.running = False

    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель подключения
        conn_frame = ttk.LabelFrame(main_frame, text="Подключение")
        conn_frame.pack(fill=tk.X, pady=5)

        ttk.Label(conn_frame, text="Сервер:").grid(row=0, column=0, padx=5)
        self.server_entry = ttk.Entry(conn_frame, width=25)
        self.server_entry.insert(0, "localhost")
        self.server_entry.grid(row=0, column=1, padx=5)

        ttk.Label(conn_frame, text="Порт:").grid(row=0, column=2, padx=5)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "65432")
        self.port_entry.grid(row=0, column=3, padx=5)

        ttk.Label(conn_frame, text="Логин:").grid(row=0, column=4, padx=5)
        self.user_entry = ttk.Entry(conn_frame, width=15)
        self.user_entry.grid(row=0, column=5, padx=5)

        ttk.Label(conn_frame, text="Пароль:").grid(row=0, column=6, padx=5)
        self.pass_entry = ttk.Entry(conn_frame, show="*", width=15)
        self.pass_entry.grid(row=0, column=7, padx=5)

        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(control_frame, text="Старт", command=self.toggle_mining)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # Статусная панель
        status_frame = ttk.LabelFrame(main_frame, text="Статус майнинга")
        status_frame.pack(fill=tk.X, pady=5)

        self.status_labels = {
            'current_block': ttk.Label(status_frame, text="Текущий блок: -"),
            'nonce_range': ttk.Label(status_frame, text="Диапазон nonce: -"),
            'difficulty': ttk.Label(status_frame, text="Сложность: -"),
            'speed': ttk.Label(status_frame, text="Скорость: 0 H/s")
        }

        for i, (_, label) in enumerate(self.status_labels.items()):
            label.grid(row=0, column=i, padx=10, pady=5)

        # Лог событий
        log_frame = ttk.LabelFrame(main_frame, text="Лог событий")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def toggle_mining(self):
        if not self.running:
            self.connect_and_start()
        else:
            self.stop_mining()

    def connect_and_start(self):
        try:
            self.client = MinerClient(
                self.server_entry.get(),
                int(self.port_entry.get()))
            self.client.username = self.user_entry.get()
            self.client.password = self.pass_entry.get()

            response = self.client.login()
            if response.get("status") != "OK":
                raise Exception(response.get("message", "Auth error"))

            self.running = True
            self.start_btn.config(text="Стоп")
            self.mining_thread = Thread(target=self.mining_loop, daemon=True)
            self.mining_thread.start()
            self.log("Майнинг запущен")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def stop_mining(self):
        self.running = False
        if self.client:
            self.client.mining = False
        self.start_btn.config(text="Старт")
        self.log("Майнинг остановлен")

    def update_status(self, task):
        if task:
            self.status_labels['current_block'].config(text=f"Текущий блок: {task['block_id']}")
            self.status_labels['nonce_range'].config(
                text=f"Диапазон nonce: {task['nonce_start']}-{task['nonce_end']}")
            self.status_labels['difficulty'].config(
                text=f"Сложность: {task['difficulty']} нулей")
        else:
            for label in self.status_labels.values():
                label.config(text=label.cget('text').split(':')[0] + ": -")

    def mining_loop(self):
        self.client.start_mining()
        last_update = 0
        hashes = 0
        task_check_interval = 2  # Проверка наличия задач каждые 2 секунды
        last_task_check = 0

        while self.running:
            try:
                # Логика обновления статуса
                if self.client.current_task:
                    self.update_status(self.client.current_task)
                    hashes += self.client.current_task['nonce_end'] - self.client.current_task['nonce_start']

                    # Обновление скорости
                    if int(current_time()) - last_update >= 1:
                        self.status_labels['speed'].config(text=f"Скорость: {hashes} H/s")
                        hashes = 0
                        last_update = int(current_time())
                else:
                    self.update_status(None)
                    # Проверка наличия задач
                    if int(current_time()) - last_task_check >= task_check_interval:
                        response = self.client.send_command("MINE")
                        if response.get("code") == "401":
                            self.log("[INFO] Нет доступных задач для майнинга")
                        last_task_check = int(current_time())

                sleep(0.1)

            except Exception as e:
                self.log(f"Ошибка: {str(e)}")
                break


if __name__ == "__main__":
    root = tk.Tk()
    app = MinerGUI(root)
    root.mainloop()