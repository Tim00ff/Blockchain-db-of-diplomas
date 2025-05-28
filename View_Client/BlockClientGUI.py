import tkinter as tk
from BlockClient import BlockClient
import json

class DiplomaViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Diploma Viewer")
        self.root.geometry("900x1200")
        self.root.configure(bg="#f0f8ff")  # Light blue background

        # Initialize with default block ID 0
        self.block_id = 0
        self.diploma_data = self.load_diploma_data(self.block_id)

        # Create the UI
        self.create_header()
        self.create_body()
        self.create_signatures()
        self.create_footer()

    def load_diploma_data(self, num=0):
        """Load diploma data from the blockchain server"""
        try:
            client = BlockClient("localhost", 65432)
            response = client.send_command(f'VIEW_BLOCK {num}')

            if response.get("status") == "OK":
                diploma_info = response["data"].get("diploma_data", {})
                print(response["data"].get("diploma_data", {}))
                return {
                    "country": "Республика Беларусь",
                    "ministry": "Министерство образования",
                    "institution": diploma_info.get("institution", ""),
                    "full_name": diploma_info.get("full_name", ""),
                    "program": diploma_info.get("program", ""),
                    "qualification": diploma_info.get("qualification", ""),
                    "specialty": diploma_info.get("specialty", ""),
                    "issue_date": diploma_info.get("issue_date", ""),
                    "reg_number": diploma_info.get("reg_number", ""),
                    "rector_name": diploma_info.get("rector_name", ""),
                    "secretary_name": diploma_info.get("secretary_name", ""),
                    "signature": diploma_info.get("signature", ""),
                    "note": "ВНИМАНИЕ: Это декоративный шаблон. Не имеет юридической силы."
                }
            else:
                return self.get_error_data(f"Server error: {response.get('message', 'Unknown error')}")

        except Exception as e:
            return self.get_error_data(str(e))

    def get_error_data(self, error_msg):
        """Fallback data when server request fails"""
        return {
            "country": "Республика Беларусь",
            "ministry": "Министерство образования",
            "institution": "Ошибка загрузки",
            "full_name": error_msg,
            "program": "",
            "qualification": "",
            "specialty": "",
            "issue_date": "",
            "reg_number": "",
            "rector_name": "",
            "secretary_name": "",
            "signature": "",
            "note": "Не удалось загрузить данные диплома"
        }

    def reload_diploma(self):
        """Reload diploma data for a new block ID"""
        try:
            new_id = int(self.block_id_entry.get())
        except ValueError:
            new_id = 0  # Default to block 0 on invalid input

        self.block_id = new_id
        self.diploma_data = self.load_diploma_data(self.block_id)

        # Rebuild the UI with new data
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_header()
        self.create_body()
        self.create_signatures()
        self.create_footer()

    def create_header(self):
        """Create the header section with country and ministry info"""
        header_frame = tk.Frame(self.root, bg="#1e3c72", padx=20, pady=15)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Country label
        country_label = tk.Label(
            header_frame,
            text=self.diploma_data["country"],
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1e3c72"
        )
        country_label.pack()

        # Ministry label
        ministry_label = tk.Label(
            header_frame,
            text=self.diploma_data["ministry"],
            font=("Arial", 16),
            fg="white",
            bg="#1e3c72"
        )
        ministry_label.pack(pady=(5, 0))

    def create_body(self):
        """Create the main body of the diploma"""
        body_frame = tk.Frame(self.root, bg="white", padx=30, pady=20)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a canvas for the seal effect
        canvas = tk.Canvas(body_frame, bg="white", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Draw a subtle seal effect
        canvas.create_oval(50, 50, 150, 150, outline="#f0f0f0", dash=(4, 4), width=2)
        canvas.create_line(100, 50, 100, 150, fill="#f0f0f0", dash=(4, 4))
        canvas.create_line(50, 100, 150, 100, fill="#f0f0f0", dash=(4, 4))

        # Create diploma content
        content_frame = tk.Frame(canvas, bg="white")
        canvas.create_window(400, 200, window=content_frame, anchor=tk.CENTER)

        # Institution
        tk.Label(
            content_frame,
            text="Учебное заведение:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        tk.Label(
            content_frame,
            text=self.diploma_data["institution"],
            font=("Arial", 12),
            bg="white"
        ).grid(row=0, column=1, sticky=tk.W, pady=(0, 5))

        # Student name
        tk.Label(
            content_frame,
            text="ФИО выпускника:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Label(
            content_frame,
            text=self.diploma_data["full_name"],
            font=("Arial", 12),
            bg="white"
        ).grid(row=1, column=1, sticky=tk.W, pady=5)

        # Program
        tk.Label(
            content_frame,
            text="Программа обучения:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        tk.Label(
            content_frame,
            text=f"«{self.diploma_data['program']}»",
            font=("Arial", 12),
            bg="white"
        ).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Qualification
        tk.Label(
            content_frame,
            text="Присвоенная квалификация:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        tk.Label(
            content_frame,
            text=self.diploma_data["qualification"],
            font=("Arial", 12),
            bg="white"
        ).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Specialty
        tk.Label(
            content_frame,
            text="Специальность:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=4, column=0, sticky=tk.W, pady=5)
        tk.Label(
            content_frame,
            text=f"«{self.diploma_data['specialty']}»",
            font=("Arial", 12),
            bg="white"
        ).grid(row=4, column=1, sticky=tk.W, pady=5)

        # Issue date
        tk.Label(
            content_frame,
            text="Дата выдачи:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=5, column=0, sticky=tk.W, pady=5)
        tk.Label(
            content_frame,
            text=self.diploma_data["issue_date"],
            font=("Arial", 12),
            bg="white"
        ).grid(row=5, column=1, sticky=tk.W, pady=5)

        # Registration number
        tk.Label(
            content_frame,
            text="Регистрационный номер:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).grid(row=6, column=0, sticky=tk.W, pady=5)
        tk.Label(
            content_frame,
            text=self.diploma_data["reg_number"],
            font=("Arial", 12),
            bg="white"
        ).grid(row=6, column=1, sticky=tk.W, pady=5)

    def create_signatures(self):
        """Create the signature section"""
        sig_frame = tk.Frame(self.root, bg="#f5f9ff", padx=20, pady=15)
        sig_frame.pack(fill=tk.X, padx=10)

        # Title
        tk.Label(
            sig_frame,
            text="Подписи:",
            font=("Arial", 12, "bold"),
            bg="#f5f9ff"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Signatures container
        sig_container = tk.Frame(sig_frame, bg="#f5f9ff")
        sig_container.pack(fill=tk.X)

        # Rector signature
        tk.Label(
            sig_container,
            text=f"Ректор/Декан: {self.diploma_data['rector_name']}",
            font=("Arial", 12),
            bg="#f5f9ff"
        ).pack(side=tk.LEFT, padx=(0, 30))

        # Secretary signature
        tk.Label(
            sig_container,
            text=f"Секретарь: {self.diploma_data['secretary_name']}",
            font=("Arial", 12),
            bg="#f5f9ff"
        ).pack(side=tk.LEFT)

        # Digital signature
        sig_frame = tk.Frame(self.root, bg="#f5f9ff", padx=20, pady=15)
        sig_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            sig_frame,
            text="Электронная подпись:",
            font=("Arial", 12, "bold"),
            bg="#f5f9ff"
        ).pack(anchor=tk.W, pady=(0, 5))

        # Signature text with monospace font and border
        sig_text = tk.Text(
            sig_frame,
            height=4,
            width=70,
            wrap=tk.WORD,
            font=("Courier", 10),
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=5
        )
        sig_text.insert(tk.END, self.diploma_data["signature"])
        sig_text.config(state=tk.DISABLED)
        sig_text.pack(fill=tk.X)

    def create_footer(self):
        """Create footer with block ID input"""
        footer_frame = tk.Frame(self.root, bg="#f0f8ff", padx=20, pady=15)
        footer_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Decorative separator
        canvas = tk.Canvas(footer_frame, height=2, bg="#f0f8ff", highlightthickness=0)
        canvas.pack(fill=tk.X, pady=5)
        canvas.create_line(50, 1, 850, 1, width=1, fill="#1e3c72", dash=(4, 2))

        # Disclaimer note
        tk.Label(
            footer_frame,
            text=self.diploma_data["note"],
            font=("Arial", 10, "italic"),
            fg="#666666",
            bg="#f0f8ff"
        ).pack(pady=(10, 0))

        # Block ID input and button
        input_frame = tk.Frame(footer_frame, bg="#f0f8ff")
        input_frame.pack(pady=(15, 5))

        tk.Label(
            input_frame,
            text="ID блока:",
            font=("Arial", 10),
            bg="#f0f8ff"
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.block_id_entry = tk.Entry(input_frame, width=10)
        self.block_id_entry.insert(0, str(self.block_id))
        self.block_id_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            input_frame,
            text="Получить",
            width=10,
            bg="#1e3c72",
            fg="white",
            relief=tk.FLAT,
            command=self.reload_diploma
        ).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiplomaViewer(root)
    root.mainloop()