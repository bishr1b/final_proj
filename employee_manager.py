import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox
from dialog import CommonDialog
from database import Employee
import csv
from tkinter import filedialog
from datetime import datetime
class EmployeeManager:
    def __init__(self, parent_frame):
        self.frame = ttkb.Frame(parent_frame, padding=10, bootstyle="light")
        self.current_employee = None
        self.setup_ui()

    def setup_ui(self):
        # Search Frame
        search_frame = ttkb.Frame(self.frame)
        search_frame.pack(fill=X, padx=10, pady=(10, 5))

        ttkb.Label(search_frame, text="🔍 Search:", font=("Helvetica", 12)).pack(side=LEFT)
        self.search_entry = ttkb.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_employees())

        # Treeview
        self.tree = ttkb.Treeview(
            self.frame,
            columns=("ID", "Name", "Role", "Phone", "Email", "Salary", "Hire Date"),
            show="headings",
            bootstyle="info",
            height=15
        )
        
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)

        for col, width in {
            "ID": 50,
            "Name": 150,
            "Role": 100,
            "Phone": 100,
            "Email": 150,
            "Salary": 100,
            "Hire Date": 120
        }.items():
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor=CENTER)

        self.tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        ttkb.Label(search_frame, text="Filter by Role:").pack(side=LEFT, padx=(15, 5))
        self.role_filter = ttkb.Combobox(search_frame, state="readonly", width=15)
        self.role_filter['values'] = ["All", "Pharmacist", "Technician", "Cashier", "Manager", "Admin"]
        self.role_filter.current(0)
        self.role_filter.pack(side=LEFT)
        self.role_filter.bind("<<ComboboxSelected>>", lambda e: self.load_employees())
        
        ttkb.Label(search_frame, text="Year:").pack(side=LEFT, padx=(10, 5))
        self.year_filter = ttkb.Combobox(search_frame, state="readonly", width=10)
        self.year_filter['values'] = ["All"] + [str(y) for y in range(2015, datetime.now().year + 1)]
        self.year_filter.current(0)
        self.year_filter.pack(side=LEFT)
        self.year_filter.bind("<<ComboboxSelected>>", lambda e: self.load_employees())
        
        # Buttons Frame
        btn_frame = ttkb.Frame(self.frame)
        btn_frame.pack(fill=X, padx=10, pady=(10, 10))

        ttkb.Button(btn_frame, text="➕ Add", command=self.show_add_dialog, bootstyle="success-outline", width=12).pack(side=LEFT, padx=5)
        self.edit_btn = ttkb.Button(btn_frame, text="✏️ Edit", command=self.show_edit_dialog, bootstyle="info-outline", width=12, state=DISABLED)
        self.edit_btn.pack(side=LEFT, padx=5)
        self.delete_btn = ttkb.Button(btn_frame, text="🗑️ Delete", command=self.delete_employee, bootstyle="danger-outline", width=12, state=DISABLED)
        self.delete_btn.pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🔄 Refresh", command=self.load_employees, bootstyle="primary-outline", width=12).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="📤 Export CSV", command=self.export_to_csv, bootstyle="warning-outline", width=12).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="📊 Stats", command=self.show_statistics, bootstyle="info-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🔄 Sort by Salary", command=self.sort_by_salary, bootstyle="info-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📊 Hire Stats", command=self.show_hiring_statistics, bootstyle="info-outline", width=14).pack(side=LEFT, padx=5)

        self.load_employees()

    def load_employees(self, search_term=None):
        self.tree.delete(*self.tree.get_children())

        try:
            # قراءة الموظفين من قاعدة البيانات
            employees = Employee.get_all(search_term or self.search_entry.get())

            # فلترة حسب الوظيفة إذا تم اختيار غير "All"
            if hasattr(self, 'role_filter'):
                role_filter = self.role_filter.get()
                if role_filter != "All":
                    employees = [e for e in employees if e['role'] == role_filter]

            # فلترة حسب سنة التوظيف إذا تم اختيار غير "All"
            if hasattr(self, 'year_filter'):
                year_filter = self.year_filter.get()
                if year_filter != "All":
                    employees = [
                        e for e in employees
                        if e['hire_date'] and e['hire_date'].year == int(year_filter)
                    ]

            # تعبئة الجدول
            for emp in employees:
                salary = f"${emp['salary']:.2f}" if emp['salary'] else "N/A"
                hire_date = emp['hire_date'].strftime("%Y-%m-%d") if emp['hire_date'] else "N/A"
                tag = "highpay" if emp['salary'] and emp['salary'] >= 2000 else ""

                self.tree.insert("", "end", values=(
                    emp['employee_id'],
                    emp['name'],
                    emp['role'] or "N/A",
                    emp['phone'] or "N/A",
                    emp['email'] or "N/A",
                    salary,
                    hire_date
                ), tags=(tag,))

            # تمييز بصري للرواتب العالية
            self.tree.tag_configure("highpay", background="", font=("Helvetica", 10, "bold"))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load employees: {str(e)}")


    def on_employee_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_employee = self.tree.item(selected[0])['values']
            self.edit_btn.config(state=NORMAL)
            self.delete_btn.config(state=NORMAL)
        else:
            self.current_employee = None
            self.edit_btn.config(state=DISABLED)
            self.delete_btn.config(state=DISABLED)

    def show_add_dialog(self):
        fields = [
            ("Name", "name", True, False, None),
            ("Role", "role", False, True, ["Pharmacist", "Technician", "Cashier", "Manager", "Admin"]),
            ("Phone", "phone", False, False, None),
            ("Email", "email", False, False, None),
            ("Salary", "salary", False, False, None),
            ("Hire Date (YYYY-MM-DD)", "hire_date", False, False, None)
        ]
        dialog = CommonDialog(self.frame, "Add New Employee", fields)
        dialog.grab_set()
        self.frame.wait_window(dialog)
        if dialog.result:
            try:
                dialog.result['salary'] = float(dialog.result['salary']) if dialog.result['salary'] else None
                Employee.create(dialog.result)
                self.load_employees()
                messagebox.showinfo("Success", "Employee added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add employee: {str(e)}")

    def show_edit_dialog(self):
        if not self.current_employee:
            return

        employee_id = self.current_employee[0]
        initial_data = {
            'name': self.current_employee[1],
            'role': self.current_employee[2],
            'phone': self.current_employee[3],
            'email': self.current_employee[4],
            'salary': float(self.current_employee[5][1:]) if self.current_employee[5] != "N/A" else None,
            'hire_date': self.current_employee[6]
        }
        fields = [
            ("Name", "name", True, False, None),
            ("Role", "role", False, True, ["Pharmacist", "Technician", "Cashier", "Manager", "Admin"]),
            ("Phone", "phone", False, False, None),
            ("Email", "email", False, False, None),
            ("Salary", "salary", False, False, None),
            ("Hire Date (YYYY-MM-DD)", "hire_date", False, False, None)
        ]
        dialog = CommonDialog(self.frame, "Edit Employee", fields, initial_data=initial_data)

        if dialog.result:
            try:
                dialog.result['salary'] = float(dialog.result['salary']) if dialog.result['salary'] else None
                Employee.update(employee_id, dialog.result)
                self.load_employees()
                messagebox.showinfo("Success", "Employee updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update employee: {str(e)}")

    def delete_employee(self):
        if not self.current_employee:
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this employee?"):
            try:
                Employee.delete(self.current_employee[0])
                self.load_employees()
                messagebox.showinfo("Success", "Employee deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete employee: {str(e)}")
                
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Write column headers
                headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                writer.writerow(headers)

                # Write data rows
                for row_id in self.tree.get_children():
                    row = self.tree.item(row_id)["values"]
                    writer.writerow(row)

            messagebox.showinfo("Success", "Data exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=getattr(self, "sort_reverse", False))

        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)

        self.sort_reverse = not getattr(self, "sort_reverse", False)
        self.sort_column = col

    def show_statistics(self):
        employees = Employee.get_all()
        total = len(employees)
        roles = {}
        salaries = []

        for emp in employees:
            role = emp['role'] or "Unknown"
            roles[role] = roles.get(role, 0) + 1
            if emp['salary']:
                salaries.append(emp['salary'])

        role_info = "\n".join(f"{role}: {count}" for role, count in roles.items())
        salary_avg = sum(salaries)/len(salaries) if salaries else 0
        salary_max = max(salaries) if salaries else 0

        msg = f"Total Employees: {total}\n\nRole Distribution:\n{role_info}\n\nAvg Salary: ${salary_avg:.2f}\nMax Salary: ${salary_max:.2f}"
        messagebox.showinfo("Employee Stats", msg)
    def sort_by_salary(self):
        data = [(float(self.tree.set(k, "Salary").replace("$", "")), k) for k in self.tree.get_children() if self.tree.set(k, "Salary") != "N/A"]
        data.sort(reverse=getattr(self, "sort_reverse", False))

        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)

        self.sort_reverse = not getattr(self, "sort_reverse", False)

    def show_hiring_statistics(self):
        """عرض عدد الموظفين حسب سنة التوظيف"""
        try:
            hiring_counts = {}
            for row_id in self.tree.get_children():
                hire_date_str = self.tree.item(row_id)['values'][6]
                if hire_date_str and hire_date_str != "N/A":
                    year = hire_date_str.split("-")[0]
                    hiring_counts[year] = hiring_counts.get(year, 0) + 1

            if not hiring_counts:
                messagebox.showinfo("Hiring Stats", "No hiring data available.")
                return

            stats = "\n".join(f"{year}: {count} employee(s)" for year, count in sorted(hiring_counts.items()))
            messagebox.showinfo("Hiring Statistics", stats)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show stats: {str(e)}")