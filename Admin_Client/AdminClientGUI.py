import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
from threading import Thread
from datetime import datetime
from AdminClient import BlockchainClient, KeyManager, DiplomaGenerator


class AdminClientGui:
    def __init__(self, root):
        self.root = root
        self.client = None
        self.key_manager = None
        self.diploma_data = {}

        root.title("Администратор дипломов")
        root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Вкладки интерфейса
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка подключения и авторизации
        self.auth_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.auth_frame, text="🔐 Авторизация")
        self.setup_auth_tab()

        # Вкладка управления ключами
        self.keys_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.keys_frame, text="🔑 Ключи")
        self.setup_keys_tab()

        # Вкладка создания диплома
        self.diploma_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.diploma_frame, text="🎓 Диплом")
        self.setup_diploma_tab()

        # Лог действий
        self.log_area = scrolledtext.ScrolledText(self.root, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def setup_auth_tab(self):
        frame = self.auth_frame
        ttk.Label(frame, text="Адрес сервера:").grid(row=0, column=0, padx=5, pady=5)
        self.server_host = ttk.Entry(frame)
        self.server_host.insert(0, "localhost")
        self.server_host.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Порт:").grid(row=1, column=0, padx=5, pady=5)
        self.server_port = ttk.Entry(frame)
        self.server_port.insert(0, "65432")
        self.server_port.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Логин:").grid(row=2, column=0, padx=5, pady=5)
        self.username = ttk.Entry(frame)
        self.username.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Пароль:").grid(row=3, column=0, padx=5, pady=5)
        self.password = ttk.Entry(frame, show="*")
        self.password.grid(row=3, column=1, padx=5, pady=5)

        self.login_btn = ttk.Button(frame, text="Войти", command=self.login)
        self.login_btn.grid(row=4, columnspan=2, pady=10)

    def setup_keys_tab(self):
        frame = self.keys_frame
        self.key_choice = tk.StringVar(value="new")

        ttk.Radiobutton(frame, text="Создать новые ключи", variable=self.key_choice, value="new"
                        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(frame, text="Использовать существующие", variable=self.key_choice, value="existing"
                        ).grid(row=1, column=0, sticky=tk.W)

        self.key_path = ttk.Entry(frame)
        self.key_path.grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(frame, text="Обзор...", command=self.browse_key_file
                   ).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Применить", command=self.handle_keys
                   ).grid(row=3, columnspan=2, pady=10)

    def setup_diploma_tab(self):
        frame = self.diploma_frame
        fields = [
            ('full_name', 'ФИО студента:'),
            ('institution', 'Учебное заведение:'),
            ('qualification', 'Степень:'),
            ('specialty', 'Специальность:'),
            ('issue_date', 'Дата выдачи (ДД.ММ.ГГГГ):'),
            ('reg_number', 'Рег. номер:'),
            ('program', 'Программа:'),
            ('rector_name', 'Ректор:'),
            ('secretary_name', 'Секретарь:')
        ]

        for i, (field, label) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            setattr(self, f"diploma_{field}", entry)

        ttk.Button(frame, text="Загрузить из файла", command=self.load_diploma_file
                   ).grid(row=len(fields), column=0, pady=10)
        ttk.Button(frame, text="Отправить данные", command=self.send_diploma
                   ).grid(row=len(fields), column=1, pady=10)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def login(self):
        def _login():
            try:
                self.client = BlockchainClient(
                    self.server_host.get(),
                    int(self.server_port.get())
                )
                response = self.client.login(
                    self.username.get(),
                    self.password.get()
                )

                if response.get("status") == "OK":
                    self.log("Успешный вход!")
                    messagebox.showinfo("Успех", "Авторизация прошла успешно!")
                else:
                    self.log(f"Ошибка входа: {response.get('message')}")
                    messagebox.showerror("Ошибка", response.get('message', 'Unknown error'))

            except Exception as e:
                self.log(f"Ошибка: {str(e)}")
                messagebox.showerror("Ошибка", str(e))

        Thread(target=_login, daemon=True).start()

    def browse_key_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.key_path.delete(0, tk.END)
            self.key_path.insert(0, path)

    def handle_keys(self):
        try:
            if self.key_choice.get() == "new":
                path = self.key_path.get()
                KeyManager().save_to_file(path)
                self.key_manager = KeyManager.from_file(path)
                self.log(f"Ключи созданы: {path}")
            else:
                self.key_manager = KeyManager.from_file(self.key_path.get())
                self.log("Ключи загружены")

            messagebox.showinfo("Успех", "Операция с ключами выполнена!")
        except Exception as e:
            self.log(f"Ошибка ключей: {str(e)}")
            messagebox.showerror("Ошибка", str(e))

    def load_diploma_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Маппинг русских заголовков на имена полей
            field_mapping = {
                'фио выпускника': 'full_name',
                'учебное заведение': 'institution',
                'программа обучения': 'program',
                'присвоенная квалификация': 'qualification',
                'специальность': 'specialty',
                'дата выдачи': 'issue_date',
                'регистрационный номер': 'reg_number',
                'ректор/декан': 'rector_name',
                'секретарь': 'secretary_name'
            }

            data = {}
            for line in content.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue

                key_part, _, value_part = line.partition(':')
                key = key_part.strip().lower()
                value = value_part.strip()

                # Поиск совпадения в маппинге
                for ru_key, field in field_mapping.items():
                    if ru_key in key:
                        data[field] = value
                        break

            # Заполнение полей в интерфейсе
            for field, value in data.items():
                entry = getattr(self, f"diploma_{field}", None)
                if entry:
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

            self.log(f"Загружено {len(data)} полей из файла: {path}")
            messagebox.showinfo("Успех", f"Данные успешно загружены из\n{path}")

        except UnicodeDecodeError:
            self.log("Ошибка: Некорректная кодировка файла")
            messagebox.showerror("Ошибка", "Файл должен быть в кодировке UTF-8")
        except Exception as e:
            self.log(f"Ошибка загрузки файла: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{str(e)}")

    def send_diploma(self):
        def _send():
            try:
                # Сбор данных из полей
                data = {
                    field: getattr(self, f"diploma_{field}").get()
                    for field in [
                        'full_name', 'institution', 'qualification',
                        'specialty', 'issue_date', 'reg_number',
                        'program', 'rector_name', 'secretary_name'
                    ]
                }

                # Создание и подпись диплома
                diploma = DiplomaGenerator(data)
                diploma.create_signature(self.key_manager)

                # Формирование команды
                command_data = {
                    "diploma_data": diploma.to_dict(),
                    "public_key": self.key_manager.get_public_pem(),
                    "signature": diploma.data['signature']
                }

                command = f"LOGIN {self.username.get()} {self.password.get()}\r\nADD_BLOCK {json.dumps(command_data)}\r\n\r\n"
                response = self.client.send_command(command)

                if response.get("status") == "OK":
                    self.log(f"Диплом отправлен! Хэш: {response['data'].get('initial_hash')}")
                    messagebox.showinfo("Успех", "Данные успешно отправлены!")
                else:
                    self.log(f"Ошибка: {response.get('message')}")
                    messagebox.showerror("Ошибка", response.get('message', 'Unknown error'))

            except Exception as e:
                self.log(f"Ошибка отправки: {str(e)}")
                messagebox.showerror("Ошибка", str(e))

        if not self.key_manager:
            messagebox.showwarning("Внимание", "Сначала настройте ключи!")
            return

        Thread(target=_send, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminClientGui(root)
    root.mainloop()