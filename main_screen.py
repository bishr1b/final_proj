import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

class MainScreen:
    def __init__(self, parent, pharmacy_app):
        self.parent = parent
        self.pharmacy_app = pharmacy_app

        self.frame = ttkb.Frame(self.parent, padding=(12, 14))
        self.frame.pack(fill=BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Title at the top
        title = ttkb.Label(
            self.frame,
            text="🏥 Welcome to Pharmacy Management System",
            font=("Helvetica", 32, "bold"),
            anchor="center",
            bootstyle="info"
        )
        title.pack(pady=30)

        # Grid Frame for buttons
        button_frame = ttkb.Frame(self.frame)
        button_frame.pack(expand=True, fill=BOTH)

        buttons_info = [
            ("💊 Medicines", "medicines"),
            ("🏢 Suppliers", "suppliers"),
            ("👥 Customers", "customers"),
            ("🛒 Orders", "orders"),
            ("📝 Prescriptions", "prescriptions"),
            ("👨‍⚕️ Employees", "employees"),
            ("📊 Analysis", "analysis"),
        ]

        rows = 3
        cols = 3

        for idx, (text, section) in enumerate(buttons_info):
            btn = ttkb.Button(
                button_frame,
                text=text,
                width=24,
                bootstyle="primary-outline",
                command=lambda m=section: self.go_to_section(m)
            )
            btn.grid(row=idx // cols, column=idx % cols, padx=20, pady=20, sticky="nsew")

        # Configure grid to be responsive
        for i in range(rows):
            button_frame.rowconfigure(i, weight=1)
        for j in range(cols):
            button_frame.columnconfigure(j, weight=1)

        # Footer Label
        footer = ttkb.Label(
            self.frame,
            text="Powered by Your Pharmacy System © 2025",
            font=("Helvetica", 10),
            bootstyle="secondary"
        )
        footer.pack(side="bottom", pady=10)

    def go_to_section(self, section_name):
        self.frame.pack_forget()
        self.pharmacy_app.show_manager(section_name)
