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
from main_screen import MainScreen  # ✅ استيراد MainScreen هنا

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1200x800")

        try:
            Database.initialize_pool()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            self.root.destroy()
            return

        # Main container
        self.main_frame = ttkb.Frame(root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Sidebar (Navigation)
        self.create_sidebar()

        # Content area
        self.content_frame = ttkb.Frame(self.main_frame, padding=10)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Initialize managers
        self.managers = {
            "medicines": MedicineManager(self.content_frame),
            "suppliers": SupplierManager(self.content_frame),
            "customers": CustomerManager(self.content_frame),
            "orders": OrderManager(self.content_frame),
            "prescriptions": PrescriptionManager(self.content_frame),
            "employees": EmployeeManager(self.content_frame)
        }

        # Initialize the Main Screen
        self.main_screen = MainScreen(self.content_frame, self)

    def create_sidebar(self):
        sidebar = ttkb.Frame(self.main_frame, width=200)
        sidebar.pack(side=LEFT, fill=Y, padx=5, pady=5)

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

        for text, manager in buttons:
            ttkb.Button(
                sidebar,
                text=text,
                command=lambda m=manager: self.navigate(m),
                width=20,
                bootstyle="secondary-outline"
            ).pack(pady=5, fill=X)

        # Exit Button
        ttkb.Button(
            sidebar,
            text="🚪 Exit",
            command=self.root.quit,
            bootstyle="danger"
        ).pack(side=BOTTOM, pady=10, fill=X)

    def navigate(self, target):
        """Handle navigation clicks"""
        # Hide all content first
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

        if target == "home":
            self.main_screen.frame.pack(fill=BOTH, expand=True)
        elif target in self.managers:
            self.managers[target].frame.pack(fill=BOTH, expand=True)
        elif target == "analysis":
            self.open_analysis()

    def show_manager(self, manager_name):
        """Called from MainScreen buttons to navigate"""
        self.navigate(manager_name)

    def open_analysis(self):
        """Open analysis window"""
        analysis_window = ttkb.Toplevel(self.root)
        AnalysisApp(analysis_window)
