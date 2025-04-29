import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import csv
from database import Supplier
from dialog import CommonDialog  # مهم جدا جدا

class SupplierManager:
    def __init__(self, parent_frame):
        self.frame = ttkb.Frame(parent_frame, padding=10, bootstyle="light")
        self.current_supplier = None
        self.selected_row = None
        self.sort_column = None
        self.sort_reverse = False
        self.setup_ui()

    def setup_ui(self):
        search_frame = ttkb.Frame(self.frame, padding=(5,5))
        search_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttkb.Label(search_frame, text="🔍 Search:", font=("Helvetica", 13, "bold")).pack(side=LEFT)
        self.search_entry = ttkb.Entry(search_frame, width=30, font=("Helvetica", 11))
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_suppliers)

        self.tree = ttkb.Treeview(
            self.frame,
            columns=("ID", "Name", "Contact", "Phone", "Email", "Country", "Terms"),
            show="headings",
            bootstyle="info",
            height=15
        )
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)

        columns = [
            ("ID", 50),
            ("Name", 150),
            ("Contact", 120),
            ("Phone", 100),
            ("Email", 150),
            ("Country", 100),
            ("Terms", 120)
        ]

        for col, width in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor=CENTER)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        btn_frame = ttkb.Frame(self.frame, padding=(0,5))
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Label(search_frame, text="🌍 Country:", font=("Helvetica", 13, "bold")).pack(side=LEFT, padx=(15, 5))
        self.country_combo = ttkb.Combobox(search_frame, font=("Helvetica", 10), width=20, state="readonly")
        self.country_combo.pack(side=LEFT)
        self.country_combo.bind("<<ComboboxSelected>>", lambda e: self.load_suppliers())

        ttkb.Button(btn_frame, text="➕ Add", command=self.add_supplier, bootstyle="success-outline", width=14, padding=(10,6)).pack(side=LEFT, padx=5)
        self.edit_btn = ttkb.Button(btn_frame, text="✏️ Edit", command=self.edit_supplier, bootstyle="info-outline", width=14, padding=(10,6), state=DISABLED)
        self.edit_btn.pack(side=LEFT, padx=5)
        self.delete_btn = ttkb.Button(btn_frame, text="🗑️ Delete", command=self.delete_supplier, bootstyle="danger-outline", width=14, padding=(10,6), state=DISABLED)
        self.delete_btn.pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📤 Export CSV", command=self.export_to_csv, bootstyle="secondary-outline", width=14, padding=(10,6)).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🔄 Refresh", command=self.load_suppliers, bootstyle="primary-outline", width=12, padding=(10,6)).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="📋 View Details", command=self.view_supplier_details, bootstyle="info-outline", width=14, padding=(10,6)).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📊 Stats", command=self.show_supplier_statistics, bootstyle="secondary-outline", width=14, padding=(10,6)).pack(side=LEFT, padx=5)
        self.load_suppliers()

    def highlight_selected_row(self):
        if self.selected_row:
            self.tree.item(self.selected_row, tags=())

        selected = self.tree.selection()
        if selected:
            self.selected_row = selected[0]
            self.tree.item(self.selected_row, tags=("highlighted",))
            self.tree.tag_configure("highlighted", background="#0078D7", foreground="white")

    def load_suppliers(self, search_term=None):
        self.tree.delete(*self.tree.get_children())

        try:
            self.suppliers = Supplier.get_all()
            filtered_suppliers = self.suppliers

            if search_term:
                term = search_term.lower()
                filtered_suppliers = [
                    sup for sup in filtered_suppliers
                    if term in str(sup.get('name', '')).lower()
                    or term in str(sup.get('contact_person', '')).lower()
                    or term in str(sup.get('phone', '')).lower()
                    or term in str(sup.get('email', '')).lower()
                    or term in str(sup.get('country', '')).lower()
                    or term in str(sup.get('payment_terms', '')).lower()
                ]

            selected_country = self.country_combo.get()
            if selected_country and selected_country != "All":
                filtered_suppliers = [
                    sup for sup in filtered_suppliers if sup.get('country') == selected_country
                ]

            for sup in filtered_suppliers:
                self.tree.insert("", ttkb.END, values=(
                    sup['supplier_id'],
                    sup['name'],
                    sup.get('contact_person', "N/A"),
                    sup.get('phone', "N/A"),
                    sup.get('email', "N/A"),
                    sup.get('country', "N/A"),
                    sup.get('payment_terms', "N/A")
                ))

            # Populate country filter combobox once
            countries = list({sup.get('country') for sup in self.suppliers if sup.get('country')})
            self.country_combo['values'] = ["All"] + sorted(countries)
            if not self.country_combo.get():
                self.country_combo.set("All")

            # Update supplier count label (if exists)
            count = len(filtered_suppliers)
            if hasattr(self, 'count_label'):
                self.count_label.config(text=f"Total: {count} suppliers")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")


    def search_suppliers(self, event=None):
        self.load_suppliers(self.search_entry.get())

    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=self.sort_reverse)

        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

        self.sort_reverse = not self.sort_reverse
        self.sort_column = col

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Suppliers As"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Contact Person", "Phone", "Email", "Country", "Payment Terms"])
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)['values'])
            messagebox.showinfo("Success", f"Suppliers exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export suppliers: {str(e)}")

    def on_select(self, event):
        self.highlight_selected_row()
        selected = self.tree.selection()
        if selected:
            self.current_supplier = self.tree.item(selected[0])['values']
            self.edit_btn.config(state=NORMAL)
            self.delete_btn.config(state=NORMAL)
        else:
            self.current_supplier = None
            self.edit_btn.config(state=DISABLED)
            self.delete_btn.config(state=DISABLED)

    def add_supplier(self):
        fields = [
            ("Name", "name", True, False, None),
            ("Contact Person", "contact_person", False, False, None),
            ("Phone", "phone", False, False, None),
            ("Email", "email", False, False, None),
            ("Country", "country", False, False, None),
            ("Payment Terms", "payment_terms", False, False, None)
        ]

        dialog = CommonDialog(self.frame, "Add Supplier", fields, align_right_labels=True)
        if dialog.result:
            try:
                Supplier.create(dialog.result)
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")

    def edit_supplier(self):
        if not self.current_supplier:
            return

        supplier_id = self.current_supplier[0]
        supplier_data = {
            'name': self.current_supplier[1],
            'contact_person': self.current_supplier[2],
            'phone': self.current_supplier[3],
            'email': self.current_supplier[4],
            'country': self.current_supplier[5],
            'payment_terms': self.current_supplier[6]
        }

        fields = [
            ("Name", "name", True, False, None),
            ("Contact Person", "contact_person", False, False, None),
            ("Phone", "phone", False, False, None),
            ("Email", "email", False, False, None),
            ("Country", "country", False, False, None),
            ("Payment Terms", "payment_terms", False, False, None)
        ]

        dialog = CommonDialog(self.frame, "Edit Supplier", fields, initial_data=supplier_data, align_right_labels=True)
        if dialog.result:
            try:
                Supplier.update(supplier_id, dialog.result)
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")

    def delete_supplier(self):
            if not self.current_supplier:
                return

            if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this supplier?", icon="warning"):
                try:
                    Supplier.delete(self.current_supplier[0])
                    self.load_suppliers()
                    messagebox.showinfo("Success", "Supplier deleted successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")
                    
    def view_supplier_details(self):
        if not self.current_supplier:
            messagebox.showwarning("No Selection", "Please select a supplier first.")
            return

        details = f"""
        🧾 Supplier Details:

        🆔 ID: {self.current_supplier[0]}
        📛 Name: {self.current_supplier[1]}
        👤 Contact: {self.current_supplier[2]}
        ☎️ Phone: {self.current_supplier[3]}
        📧 Email: {self.current_supplier[4]}
        🌍 Country: {self.current_supplier[5]}
        💵 Payment Terms: {self.current_supplier[6]}
        """

        messagebox.showinfo("Supplier Details", details)
    def show_supplier_statistics(self):
        try:
            total = len(self.suppliers)
            countries = [s.get("country", "Unknown") for s in self.suppliers]
            unique_countries = set(countries)
            most_common = max(set(countries), key=countries.count)

            messagebox.showinfo("Supplier Statistics", f"""
            📦 Total Suppliers: {total}
            🌍 Unique Countries: {len(unique_countries)}
            🏆 Most Common Country: {most_common}
            """)
        except Exception as e:
            messagebox.showerror("Error", f"Could not calculate statistics: {str(e)}")
    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=self.sort_reverse)

        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

        # تحديث عنوان العمود لإظهار رمز السهم 🔽 أو 🔼
        arrow = " 🔽" if self.sort_reverse else " 🔼"
        for heading in self.tree["columns"]:
            col_text = heading
            if heading == col:
                col_text += arrow
            self.tree.heading(heading, text=col_text, command=lambda c=heading: self.sort_by_column(c))

        self.sort_reverse = not self.sort_reverse
        self.sort_column = col


