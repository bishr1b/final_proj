import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.root = ttkb.Toplevel(master)  # Toplevel مو Window
        self.root.title("Admin Login")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.root.grab_set()  # يمنع يفتح شي ثاني قبل ما يسجل دخول

        self.login_successful = False

        self.setup_ui()

    def setup_ui(self):
        # Create main frame
        main_frame = ttkb.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=BOTH)

        # Title
        title_label = ttkb.Label(main_frame, text="Pharmacy Management System", font=("Helvetica", 22, "bold"))
        title_label.pack(pady=20)

        # Login frame
        login_frame = ttkb.LabelFrame(main_frame, text="Admin Login", padding="20")
        login_frame.pack(expand=True, fill=BOTH, padx=20, pady=10)

        # Username
        ttkb.Label(login_frame, text="Username:", font=("Helvetica", 14)).pack(fill=X, pady=10)
        self.username_entry = ttkb.Entry(login_frame, font=("Helvetica", 13))
        self.username_entry.pack(fill=X, pady=10)
        self.username_entry.focus()

        # Password
        ttkb.Label(login_frame, text="Password:", font=("Helvetica", 14)).pack(fill=X, pady=10)
        self.password_entry = ttkb.Entry(login_frame, show="*", font=("Helvetica", 13))
        self.password_entry.pack(fill=X, pady=10)

        # Login button
        login_button = ttkb.Button(login_frame, text="🔑 Login", command=self.login, bootstyle="success", width=20)
        login_button.pack(pady=20)

        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())

    def login(self):
        """Validate admin credentials"""
        ADMIN_CREDENTIALS = {
            "pharm": "pass123",
            "Shay Cormac": "EpicBruh5441",
            "bishr": "123",
            "nova": "123"
        }

        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password")
            return

        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            self.login_successful = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)

