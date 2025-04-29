import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox

from medicine_manager import MedicineManager
from supplier_manager import SupplierManager
from customer_manager import CustomerManager
from order_manager import OrderManager
from prescription_manager import PrescriptionManager
from employee_manager import EmployeeManager
from database import Database
from data_analysis import AnalysisApp
from main_screen import MainScreen

class PharmacyApp:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app

        self.root.title("Pharmacy Management System")
        self.root.geometry("1200x800")

        try:
            Database.initialize_pool()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            self.root.destroy()
            return

        self.create_styles()

        # Main Frame
        self.main_frame = ttkb.Frame(self.root, padding=10, bootstyle="light")
        self.main_frame.pack(fill=BOTH, expand=True)

        # Sidebar
        self.create_sidebar()

        # Content Area
        self.content_frame = ttkb.Frame(self.main_frame, padding=10, bootstyle="light")
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Managers
        self.managers = {
            "medicines": MedicineManager(self.content_frame),
            "suppliers": SupplierManager(self.content_frame),
            "customers": CustomerManager(self.content_frame),
            "orders": OrderManager(self.content_frame),
            "prescriptions": PrescriptionManager(self.content_frame),
            "employees": EmployeeManager(self.content_frame)
        }

        self.main_screen = MainScreen(self.content_frame, self)
        self.main_screen.frame.pack(fill=BOTH, expand=True)

    def create_styles(self):
        """Create fixed styles."""
        style = ttkb.Style()
        style.configure('Sidebar.TFrame', background="#f8f9fa")  # لون ثابت للـ Sidebar
        style.configure('Custom.TButton', font=('Helvetica', 11, 'bold'))
        style.configure('CustomOutline.TButton', font=('Helvetica', 11, 'bold'))

    def create_sidebar(self):
        """Create the fixed sidebar."""
        self.sidebar = ttkb.Frame(self.main_frame, width=220, style="Sidebar.TFrame")
        self.sidebar.pack(side=LEFT, fill=Y, padx=(0, 10), pady=5)
        self.sidebar.pack_propagate(False)

        self.sidebar.rowconfigure(0, weight=0)
        self.sidebar.rowconfigure(1, weight=1)
        self.sidebar.rowconfigure(2, weight=0)
        self.sidebar.columnconfigure(0, weight=1)

        self.theme_toggle_btn = ttkb.Button(
            self.sidebar,
            text="🌗" if self.main_app.style_name == "flatly" else "☀️",
            bootstyle="outline-light",
            width=6,
            command=self.toggle_theme,
            style="Custom.TButton"
        )
        self.theme_toggle_btn.grid(row=0, column=0, pady=(10, 10), padx=20, sticky="n")

        nav_frame = ttkb.Frame(self.sidebar)
        nav_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=5)

        buttons = [
            ("🏠 Home", "home"),
            ("💊 Medicines", "medicines"),
            ("🏢 Suppliers", "suppliers"),
            ("👥 Customers", "customers"),
            ("🛒 Orders", "orders"),
            ("📝 Prescriptions", "prescriptions"),
            ("👨‍⚕️ Employees", "employees"),
            ("📊 Analysis", "analysis"),
        ]

        self.sidebar_buttons = []

        for idx, (text, manager) in enumerate(buttons):
            btn = ttkb.Button(
                nav_frame,
                text=text,
                command=lambda m=manager, b=idx: self.navigate_with_animation(m, b),
                bootstyle="secondary",
                width=20,
                padding=(10, 6),
                style="CustomOutline.TButton"
            )
            btn.grid(row=idx, column=0, sticky="nsew", pady=4)
            self.sidebar_buttons.append((btn, manager))

        for i in range(len(buttons)):
            nav_frame.rowconfigure(i, weight=1)
        nav_frame.columnconfigure(0, weight=1)

        self.exit_btn = ttkb.Button(
            self.sidebar,
            text="🚪 Exit",
            command=self.root.quit,
            bootstyle="danger",
            width=20,
            padding=(10, 6),
            style="Custom.TButton"
        )
        self.exit_btn.grid(row=2, column=0, pady=20, padx=20, sticky="s")

    def apply_sidebar_style(self):
        """No longer needed because sidebar is fixed."""
        pass

    def toggle_theme(self):
        """Toggle between Light and Dark themes."""
        self.root.attributes("-alpha", 0.8)

        if self.main_app.style_name == "flatly":
            self.main_app.style_name = "solar"
        else:
            self.main_app.style_name = "flatly"

        self.root.style.theme_use(self.main_app.style_name)
        self.main_app.save_theme()

        self.theme_toggle_btn.config(
            text="🌗" if self.main_app.style_name == "flatly" else "☀️"
        )

        self.root.after(200, lambda: self.root.attributes("-alpha", 1.0))

    def navigate(self, target):
        """Navigate to sections."""
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

        if target == "home":
            self.main_screen.frame.pack(fill=BOTH, expand=True)
        elif target in self.managers:
            self.managers[target].frame.pack(fill=BOTH, expand=True)
        elif target == "analysis":
            self.open_analysis()

        self.highlight_sidebar(target)

    def navigate_with_animation(self, target, button_index):
        """Button shrink-then-normal animation."""
        btn, _ = self.sidebar_buttons[button_index]

        btn.configure(width=18)
        self.root.after(100, lambda: btn.configure(width=20))

        self.navigate(target)

    def highlight_sidebar(self, active_manager):
        """Highlight active button."""
        for btn, manager in self.sidebar_buttons:
            if manager == active_manager:
                btn.configure(bootstyle="primary", width=22)
            else:
                btn.configure(bootstyle="secondary", width=20)

    def show_manager(self, manager_name):
        self.navigate(manager_name)

    def open_analysis(self):
        """Open analysis window."""
        analysis_window = ttkb.Toplevel(self.root)
        AnalysisApp(analysis_window)
