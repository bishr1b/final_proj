import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime
import traceback
from database import Medicine, Supplier, Database
from dialog import CommonDialog
import csv
from tkinter import filedialog
class MedicineManager:
    def __init__(self, parent):
        self.frame = ttkb.Frame(parent, padding=10, bootstyle="light")
        self.current_medicine = None
        self.selected_row = None
        self.categories = ["All"]
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttkb.Frame(self.frame)
        top_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttkb.Label(top_frame, text="🔍 Search:").pack(side=LEFT)
        self.search_entry = ttkb.Entry(top_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_medicines())

        ttkb.Label(top_frame, text="Category:").pack(side=LEFT, padx=(15, 5))
        self.category_combo = ttkb.Combobox(top_frame, state="readonly", width=20)
        self.category_combo.pack(side=LEFT)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.load_medicines())

        self.tree = ttkb.Treeview(
            self.frame,
            columns=("ID", "Name", "Qty", "Price", "Expiry", "Category", "Supplier"),
            show="headings",
            bootstyle="info",
            height=15
        )
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)

        for col, width in {
            "ID": 50,
            "Name": 150,
            "Qty": 80,
            "Price": 80,
            "Expiry": 100,
            "Category": 100,
            "Supplier": 150,
        }.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=CENTER)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        btn_frame = ttkb.Frame(self.frame)
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Button(btn_frame, text="➕ Add", command=self.add_medicine, bootstyle="success-outline", width=14).pack(side=LEFT, padx=5)

        self.edit_btn = ttkb.Button(btn_frame, text="✏️ Edit", command=self.edit_medicine, bootstyle="info-outline", width=14, state=DISABLED)
        self.edit_btn.pack(side=LEFT, padx=5)

        self.delete_btn = ttkb.Button(btn_frame, text="🗑️ Delete", command=self.delete_medicine, bootstyle="danger-outline", width=14, state=DISABLED)
        self.delete_btn.pack(side=LEFT, padx=5)

        ttkb.Button(btn_frame, text="⏰ Expiry Check", command=self.check_expiry, bootstyle="warning-outline", width=16).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🔄 Refresh", command=self.load_medicines, bootstyle="primary-outline", width=12).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="⚠️ Highlight Low Stock", command=self.filter_low_stock, bootstyle="warning-outline", width=18).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="⬆ Sort by Price", command=self.sort_by_price, bootstyle="secondary-outline", width=16).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="⬇ Sort by Price", command=self.sort_by_price_desc, bootstyle="secondary-outline", width=16).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📤 Export CSV", command=self.export_to_csv, bootstyle="secondary-outline", width=14).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📊 Stats", command=self.show_stats, bootstyle="info-outline", width=10).pack(side=LEFT, padx=5)

        self.load_categories()
        self.load_medicines()

    def load_categories(self):
        try:
            rows = Database.fetch_all("SELECT DISTINCT category FROM medicines WHERE category IS NOT NULL")
            self.categories = ["All"] + [r['category'] for r in rows if r['category']]
            self.category_combo['values'] = self.categories
            self.category_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")

    def highlight_selected_row(self):
        if self.selected_row:
            self.tree.item(self.selected_row, tags=())
        selected = self.tree.selection()
        if selected:
            self.selected_row = selected[0]
            self.tree.item(self.selected_row, tags=("highlighted",))
            self.tree.tag_configure("highlighted", background="#0078D7", foreground="white")

    def load_medicines(self):
        search_term = self.search_entry.get()
        selected_category = self.category_combo.get()

        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            medicines = Medicine.get_all(search_term if search_term else None, include_supplier=True)
            for med in medicines:
                if selected_category != "All" and med.get('category', "N/A") != selected_category:
                    continue
                self.tree.insert("", ttkb.END, values=(
                    med['medicine_id'],
                    med['name'],
                    med['quantity'],
                    f"${med['price']:.2f}",
                    med['expiry_date'].strftime("%Y-%m-%d") if med['expiry_date'] else "N/A",
                    med['category'] or "N/A",
                    med.get('supplier_name', "N/A")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")

    def on_select(self, event):
        self.highlight_selected_row()
        selected = self.tree.selection()
        if selected:
            self.current_medicine = self.tree.item(selected[0])['values']
            self.edit_btn.config(state=NORMAL)
            self.delete_btn.config(state=NORMAL)
        else:
            self.current_medicine = None
            self.edit_btn.config(state=DISABLED)
            self.delete_btn.config(state=DISABLED)

    def check_expiry(self):
        try:
            medicines = Medicine.get_all()
            current_date = datetime.now().date()
            expired = [med for med in medicines if med['expiry_date'] and med['expiry_date'] < current_date]
            if not expired:
                messagebox.showinfo("Expiry Check", "✅ No expired medicines found!")
                return
            message = "\n".join([
                f"{med['name']} (Qty: {med['quantity']}, Expired: {med['expiry_date'].strftime('%Y-%m-%d')})"
                for med in expired
            ])
            messagebox.showwarning("Expired Medicines", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check expiry dates: {str(e)}")

    def add_medicine(self):
        fields = [
            ("Name", "name", True, False, None),
            ("Quantity", "quantity", True, False, None),
            ("Price", "price", True, False, None),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date", False, False, None),
            ("Manufacturer", "manufacturer", False, False, None),
            ("Batch Number", "batch_number", False, False, None),
            ("Category", "category", False, False, None),
            ("Description", "description", False, False, None),
            ("Supplier", "supplier_id", False, True, [f"{s['supplier_id']} - {s['name']}" for s in Supplier.get_all()])
        ]
        dialog = CommonDialog(self.frame, "Add Medicine", fields)
        if dialog.result:
            try:
                data = dialog.result
                data['price'] = float(data['price'])
                data['quantity'] = int(data['quantity'])
                data['supplier_id'] = int(data['supplier_id'].split(" - ")[0]) if data['supplier_id'] else None
                Medicine.create(data)
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")

    def edit_medicine(self):
        if not self.current_medicine:
            return
        medicine_id = self.current_medicine[0]
        try:
            medicine_data = Medicine.get_by_id(medicine_id, include_supplier=True)
            if not medicine_data:
                messagebox.showerror("Error", "Medicine not found")
                return

            fields = [
                ("Name", "name", True, False, None),
                ("Quantity", "quantity", True, False, None),
                ("Price", "price", True, False, None),
                ("Expiry Date (YYYY-MM-DD)", "expiry_date", False, False, None),
                ("Manufacturer", "manufacturer", False, False, None),
                ("Batch Number", "batch_number", False, False, None),
                ("Category", "category", False, False, None),
                ("Description", "description", False, False, None),
                ("Supplier", "supplier_id", False, True, [f"{s['supplier_id']} - {s['name']}" for s in Supplier.get_all()])
            ]
            for f in fields:
                if f[1] == "supplier_id":
                    current = medicine_data.get("supplier_id")
                    default = next((f"{s['supplier_id']} - {s['name']}" for s in Supplier.get_all() if s['supplier_id'] == current), "")
                    medicine_data["supplier_id"] = default

            dialog = CommonDialog(self.frame, "Edit Medicine", fields, initial_data=medicine_data)
            if dialog.result:
                data = dialog.result
                data['price'] = float(data['price'])
                data['quantity'] = int(data['quantity'])
                data['supplier_id'] = int(data['supplier_id'].split(" - ")[0]) if data['supplier_id'] else None
                Medicine.update(medicine_id, data)
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine updated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit medicine: {str(e)}")

    def delete_medicine(self):
        if not self.current_medicine:
            messagebox.showwarning("Warning", "No medicine selected")
            return

        if not messagebox.askyesno("Confirm Deletion", f"Delete {self.current_medicine[1]}?", icon="warning"):
            return

        try:
            medicine_id = self.current_medicine[0]
            if self.is_medicine_referenced(medicine_id):
                messagebox.showerror("Error", "Cannot delete, medicine linked with orders!")
                return

            success = Medicine.delete(medicine_id)
            if success:
                self.load_medicines()
                self.current_medicine = None
                messagebox.showinfo("Success", "Medicine deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete medicine")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")

    def is_medicine_referenced(self, medicine_id):
        try:
            result = Database.fetch_one("SELECT COUNT(*) FROM order_items WHERE medicine_id = %s", (medicine_id,))
            return result['COUNT(*)'] > 0 if result else False
        except Exception as e:
            messagebox.showerror("Error", f"Could not check references: {str(e)}")
            return True
    def sort_by_price(self):
        try:
            items = []
            for row in self.tree.get_children():
                data = self.tree.item(row)["values"]
                price = float(data[3].replace('$', ''))
                items.append((price, data))

            self.tree.delete(*self.tree.get_children())

            items.sort(reverse=False if not hasattr(self, "price_sort_reverse") or self.price_sort_reverse else True)
            self.price_sort_reverse = not getattr(self, "price_sort_reverse", False)

            for _, data in items:
                self.tree.insert("", ttkb.END, values=data)

        except Exception as e:
            messagebox.showerror("Error", f"Sort failed: {str(e)}")
            
    def sort_by_price_desc(self):
        try:
            items = []
            for row in self.tree.get_children():
                data = self.tree.item(row)["values"]
                price = float(data[3].replace('$', ''))
                items.append((price, data))

            self.tree.delete(*self.tree.get_children())

            items.sort(reverse=True)
            for _, data in items:
                self.tree.insert("", ttkb.END, values=data)

        except Exception as e:
            messagebox.showerror("Error", f"Sort failed: {str(e)}")
    def export_to_csv(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save as CSV"
            )
            if not file_path:
                return

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Quantity", "Price", "Expiry", "Category", "Supplier"])
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)['values'])

            messagebox.showinfo("Exported", f"Exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    def filter_low_stock(self):
        try:
            # أزل التمييز السابق
            for row in self.tree.get_children():
                self.tree.item(row, tags=())
            
            low_count = 0
            for row in self.tree.get_children():
                quantity_str = self.tree.item(row)['values'][2]  # العمود الثالث هو الكمية
                try:
                    quantity = int(quantity_str)
                    if quantity < 10:
                        self.tree.item(row, tags=("lowstock",))
                        low_count += 1
                except ValueError:
                    continue

            self.tree.tag_configure("lowstock", background="#FFD700")  # لون أصفر

            messagebox.showinfo("Low Stock Highlight", f"Highlighted {low_count} items with stock < 10")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter low stock: {str(e)}")

    def show_stats(self):
        try:
            medicines = Medicine.get_all()
            total = len(medicines)
            if total == 0:
                messagebox.showinfo("Statistics", "No medicines available.")
                return
            total_price = sum(m['price'] for m in medicines if m['price'])
            avg_price = total_price / total
            messagebox.showinfo("Statistics", f"📦 Total Medicines: {total}\n💲 Average Price: ${avg_price:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stats: {str(e)}")



