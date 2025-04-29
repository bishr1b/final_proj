import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from datetime import datetime
from database import Prescription, Customer
from dialog import CommonDialog
import csv

class PrescriptionManager:
    def __init__(self, parent_frame):
        self.frame = ttkb.Frame(parent_frame, padding=10, bootstyle="light")
        self.current_prescription = None
        self.selected_row = None
        self.sort_column = None
        self.sort_reverse = False
        self.setup_ui()

    def setup_ui(self):
        # Search Frame
        search_frame = ttkb.Frame(self.frame)
        search_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttkb.Label(search_frame, text="🔍 Search:", font=("Helvetica", 13, "bold")).pack(side=LEFT)
        self.search_entry = ttkb.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_prescriptions)

        # Treeview
        self.tree = ttkb.Treeview(
            self.frame,
            columns=("ID", "Customer", "Doctor", "License", "Issue", "Expiry", "Notes"),
            show="headings",
            bootstyle="info",
            height=15
        )
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)

        for col, width in {
            "ID": 50, "Customer": 150, "Doctor": 150, "License": 100,
            "Issue": 100, "Expiry": 100, "Notes": 200
        }.items():
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor=CENTER)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        # Doctor Filter
        ttkb.Label(search_frame, text="👨‍⚕️ Doctor:", font=("Helvetica", 11)).pack(side=LEFT, padx=(15, 5))
        self.doctor_filter = ttkb.Combobox(search_frame, state="readonly", width=18)
        self.doctor_filter.pack(side=LEFT)
        self.doctor_filter.bind("<<ComboboxSelected>>", self.apply_filters)

        # Customer Filter
        ttkb.Label(search_frame, text="👤 Customer:", font=("Helvetica", 11)).pack(side=LEFT, padx=(10, 5))
        self.customer_filter = ttkb.Combobox(search_frame, state="readonly", width=18)
        self.customer_filter.pack(side=LEFT)
        self.customer_filter.bind("<<ComboboxSelected>>", self.apply_filters)

        
        # Buttons Frame
        btn_frame = ttkb.Frame(self.frame)
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Button(btn_frame, text="➕ Add", command=self.add_prescription, bootstyle="success-outline", width=14).pack(side=LEFT, padx=5)
        self.edit_btn = ttkb.Button(btn_frame, text="✏️ Edit", command=self.edit_prescription, bootstyle="info-outline", width=14, state=DISABLED)
        self.edit_btn.pack(side=LEFT, padx=5)
        self.delete_btn = ttkb.Button(btn_frame, text="🗑️ Delete", command=self.delete_prescription, bootstyle="danger-outline", width=14, state=DISABLED)
        self.delete_btn.pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📊 Stats", command=self.show_statistics, bootstyle="secondary-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🔄 Refresh", command=self.load_prescriptions, bootstyle="primary-outline", width=12).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="❌ Clear Filters", command=self.clear_filters, bootstyle="danger-outline", width=12).pack(side=RIGHT, padx=5)
        ttkb.Button(btn_frame, text="⏰ Expired", command=self.show_expired_prescriptions, bootstyle="danger-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📤 Export Expired", command=self.export_expired_csv, bootstyle="warning-outline").pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="📥 Export Active", command=self.export_active_csv, bootstyle="success-outline").pack(side=LEFT, padx=5)



        
        self.load_prescriptions()

    def highlight_selected_row(self):
        if self.selected_row:
            self.tree.item(self.selected_row, tags=())
        selected = self.tree.selection()
        if selected:
            self.selected_row = selected[0]
            self.tree.item(self.selected_row, tags=("highlighted",))
            self.tree.tag_configure("highlighted", background="#0078D7", foreground="white")
            
    def format_date_safe(self, value):
            from datetime import datetime
            if hasattr(value, 'strftime'):
                return value.strftime("%Y-%m-%d")
            try:
                return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
            except:
                return value if isinstance(value, str) else "N/A"

    def load_prescriptions(self, search_term=None):
        """Load and filter prescriptions into the treeview."""
        self.tree.delete(*self.tree.get_children())

        try:
            self.prescriptions = Prescription.get_all()
            filtered = self.prescriptions

            # Apply search term filter if provided
            if search_term:
                term = search_term.lower()
                filtered = []
                for pres in self.prescriptions:
                    if (
                        term in str(pres['prescription_id']).lower()
                        or term in str(pres.get('doctor_name', '')).lower()
                        or term in str(pres.get('doctor_license', '')).lower()
                        or term in str(pres.get('customer_name', '')).lower()
                        or term in (pres.get('issue_date') or "").strftime("%Y-%m-%d").lower()
                        or (pres.get('expiry_date') and term in pres['expiry_date'].strftime("%Y-%m-%d").lower())
                    ):
                        filtered.append(pres)

            # Fill tree with (possibly filtered) data
            for pres in filtered:
                self.tree.insert("", ttkb.END, values=(
                    pres['prescription_id'],
                    pres.get('customer_name', "N/A"),
                    pres.get('doctor_name', "N/A"),
                    pres.get('doctor_license', "N/A"),
                    self.format_date_safe(pres.get('issue_date')),
                    self.format_date_safe(pres.get('expiry_date')),
                    pres.get('notes', "N/A")
                ))

            # Populate doctor and customer filters
            doctor_names = sorted(set(p.get("doctor_name", "N/A") for p in self.prescriptions))
            customer_names = sorted(set(p.get("customer_name", "N/A") for p in self.prescriptions))

            self.doctor_filter['values'] = ["All"] + doctor_names
            self.customer_filter['values'] = ["All"] + customer_names

            self.doctor_filter.set("All")
            self.customer_filter.set("All")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prescriptions: {str(e)}")
            self.tree.delete(*self.tree.get_children())
            try:
                prescriptions = Prescription.get_all()
                filtered = prescriptions

                if search_term:
                    term = search_term.lower()
                    filtered = [
                        pres for pres in prescriptions
                        if term in str(pres['prescription_id']).lower()
                        or term in str(pres.get('doctor_name', '')).lower()
                        or term in str(pres.get('doctor_license', '')).lower()
                        or term in str(pres.get('customer_name', '')).lower()
                        or term in (pres.get('issue_date') or '').strftime("%Y-%m-%d").lower()
                        or (pres.get('expiry_date') and term in pres['expiry_date'].strftime("%Y-%m-%d").lower())
                    ]

                for pres in filtered:
                    self.tree.insert("", ttkb.END, values=(
                        pres['prescription_id'],
                        pres.get('customer_name', "N/A"),
                        pres.get('doctor_name', "N/A"),
                        pres.get('doctor_license', "N/A"),
                        pres.get('issue_date').strftime("%Y-%m-%d") if pres.get('issue_date') else "N/A",
                        pres.get('expiry_date').strftime("%Y-%m-%d") if pres.get('expiry_date') else "N/A",
                        pres.get('notes', "N/A")
                    ))

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load prescriptions: {str(e)}")

    def search_prescriptions(self, event=None):
        self.load_prescriptions(self.search_entry.get())

    def on_select(self, event):
        self.highlight_selected_row()
        selected = self.tree.selection()
        if selected:
            self.current_prescription = self.tree.item(selected[0])['values']
            self.edit_btn.config(state=NORMAL)
            self.delete_btn.config(state=NORMAL)
        else:
            self.current_prescription = None
            self.edit_btn.config(state=DISABLED)
            self.delete_btn.config(state=DISABLED)

    def add_prescription(self):
        customers = Customer.get_all()
        customer_names = [f"{c['customer_id']} - {c['name']}" for c in customers]

        fields = [
            ("Customer", "customer_id", True, True, customer_names),
            ("Doctor Name", "doctor_name", True, False, None),
            ("Doctor License", "doctor_license", False, False, None),
            ("Issue Date (YYYY-MM-DD)", "issue_date", True, False, None),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date", False, False, None),
            ("Notes", "notes", False, False, None),
        ]

        dialog = CommonDialog(self.frame, "Add Prescription", fields, align_right_labels=True)

        if dialog.result:
            try:
                cid = int(dialog.result['customer_id'].split(' - ')[0])
                data = {
                    'customer_id': cid,
                    'doctor_name': dialog.result['doctor_name'],
                    'doctor_license': dialog.result['doctor_license'] or None,
                    'issue_date': dialog.result['issue_date'],
                    'expiry_date': dialog.result['expiry_date'] or None,
                    'notes': dialog.result['notes'] or None,
                }
                Prescription.create(data)
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add prescription: {str(e)}")

    def edit_prescription(self):
        if not self.current_prescription:
            return

        prescription_id = self.current_prescription[0]
        try:
            presc = Prescription.get_by_id(prescription_id)
            customers = Customer.get_all()
            customer_names = [f"{c['customer_id']} - {c['name']}" for c in customers]
            cid_str = next((f"{c['customer_id']} - {c['name']}" for c in customers if c['customer_id'] == presc['customer_id']), "")

            fields = [
                ("Customer", "customer_id", True, True, customer_names),
                ("Doctor Name", "doctor_name", True, False, None),
                ("Doctor License", "doctor_license", False, False, None),
                ("Issue Date (YYYY-MM-DD)", "issue_date", True, False, None),
                ("Expiry Date (YYYY-MM-DD)", "expiry_date", False, False, None),
                ("Notes", "notes", False, False, None),
            ]

            initial_data = {
                'customer_id': cid_str,
                'doctor_name': presc['doctor_name'],
                'doctor_license': presc['doctor_license'],
                'issue_date': presc['issue_date'].strftime("%Y-%m-%d"),
                'expiry_date': presc['expiry_date'].strftime("%Y-%m-%d") if presc['expiry_date'] else "",
                'notes': presc['notes'] or ""
            }

            dialog = CommonDialog(self.frame, "Edit Prescription", fields, initial_data, align_right_labels=True)

            if dialog.result:
                cid = int(dialog.result['customer_id'].split(' - ')[0])
                updated_data = {
                    'customer_id': cid,
                    'doctor_name': dialog.result['doctor_name'],
                    'doctor_license': dialog.result['doctor_license'] or None,
                    'issue_date': dialog.result['issue_date'],
                    'expiry_date': dialog.result['expiry_date'] or None,
                    'notes': dialog.result['notes'] or None
                }
                Prescription.update(prescription_id, updated_data)
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription updated successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit prescription: {str(e)}")

    def delete_prescription(self):
        if not self.current_prescription:
            return

        if messagebox.askyesno("Confirm", "Delete this prescription?", icon="warning"):
            try:
                Prescription.delete(self.current_prescription[0])
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete prescription: {str(e)}")

    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=self.sort_reverse)
        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)
        self.sort_reverse = not self.sort_reverse
        self.sort_column = col

    

    def show_statistics(self):
        try:
            total = len(self.tree.get_children())
            expired = sum(1 for i in self.tree.get_children() if self.tree.item(i)['values'][5] != "N/A" and datetime.strptime(self.tree.item(i)['values'][5], "%Y-%m-%d").date() < datetime.today().date())
            messagebox.showinfo("Prescription Stats", f"Total: {total}\nExpired: {expired}")
        except Exception as e:
            messagebox.showerror("Stats Error", str(e))
            
    def filter_prescriptions(self, event=None):
        doctor_term = self.doctor_filter.get().strip().lower()
        customer_term = self.customer_filter.get().strip().lower()

        filtered = [
            p for p in self.prescriptions
            if doctor_term in p.get("doctor_name", "").lower()
            and customer_term in p.get("customer_name", "").lower()
        ]

        self.tree.delete(*self.tree.get_children())

        for pres in filtered:
            self.tree.insert("", ttkb.END, values=(
                pres['prescription_id'],
                pres.get('customer_name', "N/A"),
                pres.get('doctor_name', "N/A"),
                pres.get('doctor_license', "N/A"),
                pres.get('issue_date').strftime("%Y-%m-%d") if pres.get('issue_date') else "N/A",
                pres.get('expiry_date').strftime("%Y-%m-%d") if pres.get('expiry_date') else "N/A",
                pres.get('notes', "N/A")
            ))
    def apply_filters(self, event=None):
        doctor_selected = self.doctor_filter.get()
        customer_selected = self.customer_filter.get()

        filtered = self.prescriptions

        # تصفية البيانات حسب الطبيب
        if doctor_selected and doctor_selected != "All":
            filtered = [p for p in filtered if p.get("doctor_name") == doctor_selected]

        # تصفية البيانات حسب العميل
        if customer_selected and customer_selected != "All":
            filtered = [p for p in filtered if p.get("customer_name") == customer_selected]

        # تحديث قائمة العملاء أو الأطباء حسب الآخر
        if event and event.widget == self.doctor_filter:
            customers = sorted(set(p.get("customer_name", "N/A") for p in filtered))
            self.customer_filter['values'] = ["All"] + customers
            if self.customer_filter.get() not in customers:
                self.customer_filter.set("All")

        elif event and event.widget == self.customer_filter:
            doctors = sorted(set(p.get("doctor_name", "N/A") for p in filtered))
            self.doctor_filter['values'] = ["All"] + doctors
            if self.doctor_filter.get() not in doctors:
                self.doctor_filter.set("All")

        # عرض النتائج في الجدول
        self.tree.delete(*self.tree.get_children())
        for pres in filtered:
            self.tree.insert("", ttkb.END, values=(
                pres['prescription_id'],
                pres.get('customer_name', "N/A"),
                pres.get('doctor_name', "N/A"),
                pres.get('doctor_license', "N/A"),
                self.format_date_safe(pres.get('issue_date')),
                self.format_date_safe(pres.get('expiry_date')),
                pres.get('notes', "N/A")
            ))

    def clear_filters(self):
        """Clear doctor and customer filters and reload data."""
        if hasattr(self, "doctor_filter"):
            self.doctor_filter.set("All")
        if hasattr(self, "customer_filter"):
            self.customer_filter.set("All")
        self.load_prescriptions()
        



    def show_expired_prescriptions(self):
        from datetime import datetime

        self.tree.delete(*self.tree.get_children())
        today = datetime.today().date()
        expired = []

        most_common_doctor = {}
        most_common_customer = {}

        for pres in self.prescriptions:
            expiry = pres.get("expiry_date")
            if expiry and isinstance(expiry, datetime) and expiry.date() < today:
                expired.append(pres)

                # Count doctors and customers
                doc = pres.get("doctor_name", "N/A")
                most_common_doctor[doc] = most_common_doctor.get(doc, 0) + 1

                cust = pres.get("customer_name", "N/A")
                most_common_customer[cust] = most_common_customer.get(cust, 0) + 1

        # Sort most frequent doctor/customer
        top_doc = max(most_common_doctor, key=most_common_doctor.get) if most_common_doctor else "N/A"
        top_cust = max(most_common_customer, key=most_common_customer.get) if most_common_customer else "N/A"

        # Insert expired prescriptions with highlight
        for pres in expired:
            expired_date = pres['expiry_date'].date()
            days_ago = (today - expired_date).days
            self.tree.insert("", ttkb.END, values=(
                pres['prescription_id'],
                pres.get('customer_name', "N/A"),
                pres.get('doctor_name', "N/A"),
                pres.get('doctor_license', "N/A"),
                self.format_date_safe(pres.get('issue_date')),
                f"{self.format_date_safe(pres.get('expiry_date'))} ({days_ago} days ago)",
                pres.get('notes', "N/A")
            ), tags=("expired",))

        self.tree.tag_configure("expired", background="#FFECEC", foreground="#C0392B", font=("Helvetica", 10, "bold"))

        # Summary info
        messagebox.showinfo(
            "Expired Prescriptions",
            f"Total expired prescriptions: {len(expired)}\n"
            f"Most expired by Doctor: {top_doc}\n"
            f"Most expired for Customer: {top_cust}"
        )
    def export_expired_csv(self):
        from datetime import datetime, date
        expired = [
            pres for pres in self.prescriptions
            if pres.get("expiry_date") and isinstance(pres["expiry_date"], (datetime, date)) and pres["expiry_date"] < date.today()
        ]

        if not expired:
            messagebox.showinfo("No Expired", "No expired prescriptions found.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Export Expired Prescriptions")
        if not file_path:
            return

        try:
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["ID", "Customer", "Doctor", "License", "Issue", "Expiry", "Notes"])
                for pres in expired:
                    writer.writerow([
                        pres['prescription_id'],
                        pres.get('customer_name', "N/A"),
                        pres.get('doctor_name', "N/A"),
                        pres.get('doctor_license', "N/A"),
                        self.format_date_safe(pres.get('issue_date')),
                        self.format_date_safe(pres.get('expiry_date')),
                        pres.get('notes', "N/A")
                    ])
            messagebox.showinfo("Exported", f"Expired prescriptions saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
    def export_active_csv(self):
        from datetime import datetime, date
        active = [
            pres for pres in self.prescriptions
            if not pres.get("expiry_date") or pres["expiry_date"] >= date.today()
        ]

        if not active:
            messagebox.showinfo("No Active", "No active prescriptions found.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Export Active Prescriptions")
        if not file_path:
            return

        try:
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["ID", "Customer", "Doctor", "License", "Issue", "Expiry", "Notes"])
                for pres in active:
                    writer.writerow([
                        pres['prescription_id'],
                        pres.get('customer_name', "N/A"),
                        pres.get('doctor_name', "N/A"),
                        pres.get('doctor_license', "N/A"),
                        self.format_date_safe(pres.get('issue_date')),
                        self.format_date_safe(pres.get('expiry_date')),
                        pres.get('notes', "N/A")
                    ])
            messagebox.showinfo("Exported", f"Active prescriptions saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
