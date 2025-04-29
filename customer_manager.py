import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from database import Customer, Order, Prescription
from dialog import CommonDialog

class CustomerManager:
    def __init__(self, parent):
        self.frame = ttkb.Frame(parent, padding=10, bootstyle="light")
        self.current_customer = None
        self.selected_row = None
        self.sort_points_reverse = False  
        self.sort_by_age_reverse = False
        self.setup_ui()
        

    def setup_ui(self):
        # ===== Search Frame =====
        search_frame = ttkb.Frame(self.frame)
        search_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttkb.Label(search_frame, text="🔍 Search:", font=("Helvetica", 13, "bold")).pack(side=LEFT)
        self.search_entry = ttkb.Entry(search_frame, width=30, font=("Helvetica", 11))
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_customers)

        # ===== Treeview =====
        self.tree = ttkb.Treeview(
            self.frame,
            columns=("ID", "Name", "Phone", "Email", "Address", "Age", "Points"),
            show="headings",
            bootstyle="info",
            height=15
        )
        self.tree.tag_configure("vip", background="", font=("Helvetica", 10, "bold"))
        self.tree.tag_configure("regular", background="", font=("Helvetica", 10))
        self.tree.tag_configure("highlighted", background="#0078D7", foreground="white")
        
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.tree.heading("Age", text="Age", command=self.sort_by_age)
        self.tree.heading("Points", text="Loyalty Points", command=self.sort_by_loyalty_points)
        columns = [
            ("ID", 50),
            ("Name", 150),
            ("Phone", 100),
            ("Email", 150),
            ("Address", 200),
            ("Age", 50),
            ("Points", 100)
        ]

        for col, width in columns:
            self.tree.heading(col, text=col)
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))

        self.tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
        ttkb.Label(search_frame, text="Min Points:").pack(side=LEFT, padx=(15, 5))
        self.points_filter = ttkb.Combobox(search_frame, width=10, state="readonly")
        self.points_filter['values'] = ["All", ">= 100", ">= 500", ">= 1000"]
        self.points_filter.current(0)
        self.points_filter.pack(side=LEFT)
        self.points_filter.bind("<<ComboboxSelected>>", lambda e: self.load_customers())
        # ===== Buttons Frame =====
        btn_frame = ttkb.Frame(self.frame, padding=(0,5))
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Button(btn_frame, text="➕ Add", command=self.add_customer, bootstyle="success-outline", width=14, padding=(10,6)).pack(side=LEFT, padx=5)
        self.edit_btn = ttkb.Button(btn_frame, text="✏️ Edit", command=self.edit_customer, bootstyle="info-outline", width=14, padding=(10,6), state=DISABLED)
        self.edit_btn.pack(side=LEFT, padx=5)
        self.delete_btn = ttkb.Button(btn_frame, text="🗑️ Delete", command=self.delete_customer, bootstyle="danger-outline", width=14, padding=(10,6), state=DISABLED)
        self.delete_btn.pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📥 Export CSV", command=self.export_to_csv, bootstyle="secondary-outline", width=14, padding=(10,6)).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🔄 Refresh", command=self.load_customers, bootstyle="primary-outline", width=12, padding=(10,6)).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="📄 View", command=self.print_customer_details, bootstyle="info-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📊 Stats", command=self.show_statistics, bootstyle="info-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="💳 Points", command=self.show_loyalty_points, bootstyle="info-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="👵 Age Dist.", command=self.show_age_distribution, bootstyle="info-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="⬇️ Sort by Points", command=self.sort_by_loyalty_points,
            bootstyle="info-outline", width=16, padding=(10,6)).pack(side=LEFT, padx=5)

        self.load_customers()

    def load_customers(self, search_term=None):
        self.tree.delete(*self.tree.get_children())
        try:
            customers = Customer.get_all(search_term)
            
            # فلتر حسب نقاط الولاء
            selected_filter = self.points_filter.get()
            if selected_filter != "All":
                min_points = int(selected_filter.replace(">=", "").strip())
                customers = [c for c in customers if c['loyalty_points'] and int(c['loyalty_points']) >= min_points]

            for cust in customers:
                points = cust['loyalty_points'] or 0
                tag = "vip" if points >= 1000 else "regular"

                self.tree.insert("", ttkb.END, values=(
                    cust['customer_id'],
                    cust['name'],
                    cust['phone'] or "N/A",
                    cust['email'] or "N/A",
                    cust['address'] or "N/A",
                    cust['age'] or "N/A",
                    points
                ), tags=(tag,))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")



    def search_customers(self, event=None):
        self.load_customers(self.search_entry.get())

    def on_customer_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_customer = self.tree.item(selected[0])['values']
            self.edit_btn.config(state=NORMAL)
            self.delete_btn.config(state=NORMAL)
        else:
            self.current_customer = None
            self.edit_btn.config(state=DISABLED)
            self.delete_btn.config(state=DISABLED)

    def add_customer(self):
        fields = [
            ("Name", "name", True, False, None),
            ("Phone", "phone", False, False, None),
            ("Email", "email", False, False, None),
            ("Address", "address", False, False, None),
            ("Age", "age", False, False, None),
            ("Loyalty Points", "loyalty_points", False, False, None)
        ]
        dialog = CommonDialog(self.frame, "Add Customer", fields, align_right_labels=True)
        if dialog.result:
            try:
                dialog.result['age'] = int(dialog.result['age']) if dialog.result['age'] else None
                dialog.result['loyalty_points'] = int(dialog.result['loyalty_points']) if dialog.result['loyalty_points'] else 0
                Customer.create(dialog.result)
                self.load_customers()
                messagebox.showinfo("Success", "Customer added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")

    def edit_customer(self):
        if not self.current_customer:
            return

        customer_id = self.current_customer[0]
        data = {
            'name': self.current_customer[1],
            'phone': self.current_customer[2],
            'email': self.current_customer[3],
            'address': self.current_customer[4],
            'age': self.current_customer[5],
            'loyalty_points': self.current_customer[6]
        }

        fields = [
            ("Name", "name", True, False, None),
            ("Phone", "phone", False, False, None),
            ("Email", "email", False, False, None),
            ("Address", "address", False, False, None),
            ("Age", "age", False, False, None),
            ("Loyalty Points", "loyalty_points", False, False, None)
        ]

        dialog = CommonDialog(self.frame, "Edit Customer", fields, initial_data=data, align_right_labels=True)
        if dialog.result:
            try:
                dialog.result['age'] = int(dialog.result['age']) if dialog.result['age'] else None
                dialog.result['loyalty_points'] = int(dialog.result['loyalty_points']) if dialog.result['loyalty_points'] else 0
                Customer.update(customer_id, dialog.result)
                self.load_customers()
                messagebox.showinfo("Success", "Customer updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {str(e)}")

    def delete_customer(self):
        if not self.current_customer:
            return

        if messagebox.askyesno("Confirm", "Delete this customer and all related data?", icon="warning"):
            try:
                customer_id = self.current_customer[0]
                Order.delete_by_customer_id(customer_id)
                Prescription.delete_by_customer_id(customer_id)
                Customer.delete(customer_id)
                self.load_customers()
                messagebox.showinfo("Success", "Customer deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")

    def export_to_csv(self):
        """Export customer data to CSV."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Customers"
        )

        if not file_path:
            return

        try:
            import csv
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Phone", "Email", "Address", "Age", "Loyalty Points"])
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)['values'])

            messagebox.showinfo("Exported", f"Customer data saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=getattr(self, "sort_reverse", False))

        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)

        self.sort_reverse = not getattr(self, "sort_reverse", False)
        self.sort_column = col
    def print_customer_details(self):
        if not self.current_customer:
            messagebox.showwarning("Warning", "Select a customer first.")
            return

        cust = self.current_customer
        details = f"""
        👤 Name: {cust[1]}
        📞 Phone: {cust[2]}
        📧 Email: {cust[3]}
        🏠 Address: {cust[4]}
        🎂 Age: {cust[5]}
        ⭐ Points: {cust[6]}
        """
        messagebox.showinfo("Customer Details", details.strip())
    def show_statistics(self):
        total_customers = len(self.tree.get_children())
        vip_customers = sum(
            1 for item in self.tree.get_children()
            if int(self.tree.item(item)['values'][6]) >= 1000
        )
        regular_customers = total_customers - vip_customers

        message = (
            f"📋 Total Customers: {total_customers}\n"
            f"🌟 VIP Customers (≥ 1000 pts): {vip_customers}\n"
            f"👥 Regular Customers: {regular_customers}"
        )
        messagebox.showinfo("Customer Summary", message)

    def show_loyalty_points(self):
        total = sum(int(self.tree.item(i)['values'][6]) for i in self.tree.get_children())
        average = total / len(self.tree.get_children()) if self.tree.get_children() else 0
        message = (
            f"🏆 Total Loyalty Points: {total}\n"
            f"📈 Average Points per Customer: {average:.2f}"
        )
        messagebox.showinfo("Loyalty Points", message)

    def show_age_distribution(self):
        from collections import defaultdict

        age_groups = defaultdict(int)
        for i in self.tree.get_children():
            age = self.tree.item(i)['values'][5]
            try:
                age = int(age)
                if age < 18:
                    group = "< 18"
                elif age < 30:
                    group = "18–29"
                elif age < 45:
                    group = "30–44"
                elif age < 60:
                    group = "45–59"
                else:
                    group = "60+"
                age_groups[group] += 1
            except:
                continue

        if not age_groups:
            messagebox.showinfo("Age Distribution", "No valid age data available.")
            return

        distribution = "\n".join(f"{grp}: {count} customer(s)" for grp, count in sorted(age_groups.items()))
        messagebox.showinfo("Age Group Distribution", distribution)
    def sort_by_loyalty_points(self):
        """Sort the treeview by Loyalty Points."""
        rows = [(self.tree.set(k, "Points"), k) for k in self.tree.get_children()]
        try:
            # التأكد من القيم صحيحة للفرز
            rows.sort(key=lambda x: int(x[0]), reverse=self.sort_points_reverse)
        except ValueError:
            messagebox.showerror("Error", "Invalid point values in data")
            return

        for index, (_, k) in enumerate(rows):
            self.tree.move(k, '', index)

        self.sort_points_reverse = not self.sort_points_reverse
    def sort_by_age(self):
        data = [
            (self.tree.set(item, "Age"), item)
            for item in self.tree.get_children()
            if self.tree.set(item, "Age") != "N/A"
        ]

        try:
            data = [(int(age), item) for age, item in data]
            data.sort(reverse=self.sort_by_age_reverse)

            for idx, (_, item) in enumerate(data):
                self.tree.move(item, '', idx)

            # تحديث عنوان العمود
            arrow = "🔽" if self.sort_by_age_reverse else "🔼"
            self.tree.heading("Age", text=f"Age {arrow}", command=self.sort_by_age)

            # عكس الاتجاه للنقرة القادمة
            self.sort_by_age_reverse = not self.sort_by_age_reverse

        except Exception as e:
            messagebox.showerror("Error", f"Sorting error: {str(e)}")