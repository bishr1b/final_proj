import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime
from database import Order, Medicine, Customer, Employee, Database
from PIL import Image, ImageDraw, ImageFont
import os
import tkinter as tk
import subprocess

class OrderManager:
    def __init__(self, parent_frame, on_order_saved=None):
        self.frame = ttkb.Frame(parent_frame, padding=10, bootstyle="light")
        self.current_order = None
        self.order_items = []
        self.on_order_saved = on_order_saved
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttkb.Frame(self.frame)
        top_frame.pack(fill=X, padx=10, pady=(0, 10))

        order_info = ttkb.LabelFrame(top_frame, text="📝 Order Information", padding=10, bootstyle="info")
        order_info.pack(side=LEFT, padx=5, fill=Y)

        ttkb.Label(order_info, text="Customer:", font=("Helvetica", 11)).grid(row=0, column=0, sticky=E, pady=5)
        self.customer_combo = ttkb.Combobox(order_info, width=30, font=("Helvetica", 10))
        self.customer_combo.grid(row=0, column=1, pady=5)

        ttkb.Label(order_info, text="Employee:", font=("Helvetica", 11)).grid(row=1, column=0, sticky=E, pady=5)
        self.employee_combo = ttkb.Combobox(order_info, width=30, font=("Helvetica", 10))
        self.employee_combo.grid(row=1, column=1, pady=5)

        ttkb.Label(order_info, text="Order Type:", font=("Helvetica", 11)).grid(row=2, column=0, sticky=E, pady=5)
        self.order_type_combo = ttkb.Combobox(order_info, values=["Retail", "Wholesale", "Online"], width=30, font=("Helvetica", 10))
        self.order_type_combo.grid(row=2, column=1, pady=5)
        self.order_type_combo.current(0)

        add_item = ttkb.LabelFrame(top_frame, text="➕ Add Item", padding=10, bootstyle="success")
        add_item.pack(side=LEFT, padx=5, fill=Y)

        ttkb.Label(add_item, text="Medicine:", font=("Helvetica", 11)).grid(row=0, column=0, sticky=E, pady=5)
        self.medicine_combo = ttkb.Combobox(add_item, width=30, font=("Helvetica", 10))
        self.medicine_combo.grid(row=0, column=1, pady=5)

        ttkb.Label(add_item, text="Quantity:", font=("Helvetica", 11)).grid(row=1, column=0, sticky=E, pady=5)
        self.quantity_entry = ttkb.Entry(add_item, width=33, font=("Helvetica", 10))
        self.quantity_entry.grid(row=1, column=1, pady=5)

        ttkb.Button(add_item, text="➕ Add Item", command=self.add_item, bootstyle="success-outline", width=20).grid(row=2, column=1, pady=10)

        items_frame = ttkb.LabelFrame(self.frame, text="📋 Order Items", padding=10, bootstyle="info")
        items_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        self.items_tree = ttkb.Treeview(
            items_frame,
            columns=("Medicine", "Quantity", "Price", "Subtotal"),
            show="headings",
            bootstyle="primary",
            height=10
        )
        self.items_tree.pack(fill=BOTH, expand=True)

        for col, width in {"Medicine": 200, "Quantity": 80, "Price": 100, "Subtotal": 100}.items():
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=width, anchor=CENTER)

        bottom_frame = ttkb.Frame(self.frame)
        bottom_frame.pack(fill=X, padx=10)

        self.total_label = ttkb.Label(bottom_frame, text="Total: $0.00", font=("Helvetica", 13, "bold"), bootstyle="inverse-info")
        self.total_label.pack(side=LEFT, padx=5)

        btn_frame = ttkb.Frame(bottom_frame)
        btn_frame.pack(side=RIGHT)

        ttkb.Button(btn_frame, text="🆕 New Order", command=self.new_order, bootstyle="primary-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="💾 Save Order", command=self.save_order, bootstyle="success-outline", width=12).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🖨️ Generate & Print Bill", command=self.generate_bill, bootstyle="warning-outline", width=18).pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="🗑️ Delete Item", command=self.delete_item, bootstyle="danger-outline", width=12).pack(side=LEFT, padx=5)

        self.load_combos()
        self.new_order()

    def load_combos(self):
        try:
            customers = Customer.get_all()
            self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]
            if customers:
                self.customer_combo.current(0)

            employees = Employee.get_all()
            self.employee_combo['values'] = [f"{e['employee_id']} - {e['name']}" for e in employees]
            if employees:
                self.employee_combo.current(0)

            medicines = Medicine.get_all()
            self.medicine_combo['values'] = [f"{m['medicine_id']} - {m['name']}" for m in medicines]
            if medicines:
                self.medicine_combo.current(0)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def new_order(self):
        self.order_items = []
        self.update_items_tree()
        self.customer_combo.set('')
        self.employee_combo.set('')
        self.order_type_combo.current(0)
        self.total_label.config(text="Total: $0.00")

    def add_item(self):
        medicine = self.medicine_combo.get()
        quantity = self.quantity_entry.get()
        if not medicine or not quantity:
            messagebox.showwarning("Warning", "Please select medicine and enter quantity")
            return
        try:
            medicine_id = int(medicine.split(" - ")[0])
            quantity = int(quantity)
            med = Medicine.get_by_id(medicine_id)
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
            if quantity > med['quantity']:
                messagebox.showerror("Error", f"Only {med['quantity']} available in stock")
                return
            price = float(med['price'])
            self.order_items.append({
                'medicine_id': medicine_id,
                'name': med['name'],
                'quantity': quantity,
                'price': price,
                'subtotal': price * quantity
            })
            self.update_items_tree()
            self.medicine_combo.set('')
            self.quantity_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def update_items_tree(self):
        self.items_tree.delete(*self.items_tree.get_children())
        total = 0.0
        for item in self.order_items:
            self.items_tree.insert('', END, values=(item['name'], item['quantity'], f"${item['price']:.2f}", f"${item['subtotal']:.2f}"))
            total += item['subtotal']
        self.total_label.config(text=f"Total: ${total:.2f}")

    def delete_item(self):
        selected = self.items_tree.selection()
        if selected:
            index = self.items_tree.index(selected[0])
            if 0 <= index < len(self.order_items):
                self.order_items.pop(index)
                self.update_items_tree()

    def save_order(self):
        if not self.order_items:
            messagebox.showwarning("Warning", "No items in order")
            return
        customer = self.customer_combo.get()
        employee = self.employee_combo.get()
        if not customer or not employee:
            messagebox.showwarning("Warning", "Fill customer and employee fields")
            return
        conn = None
        try:
            customer_id = int(customer.split(" - ")[0])
            employee_id = int(employee.split(" - ")[0])
            order_data = {
                'customer_id': customer_id,
                'employee_id': employee_id,
                'order_type': self.order_type_combo.get(),
                'total_amount': sum(i['subtotal'] for i in self.order_items),
                'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            conn = Database.get_connection()
            order_id = Order.create_with_details(order_data, self.order_items)
            if not order_id:
                raise Exception("Order creation failed")
            for item in self.order_items:
                Medicine.reduce_stock(item['medicine_id'], item['quantity'])
            Customer.add_loyalty_points(customer_id, int(order_data['total_amount'] * 10))
            conn.commit()
            messagebox.showinfo("Success", f"Order #{order_id} saved!")
            self.new_order()
            if self.on_order_saved:
                self.on_order_saved()
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            if conn:
                Database.close_connection(conn)

    def generate_bill(self):
        if not self.order_items:
            messagebox.showwarning("Warning", "No items to generate bill")
            return

        folder = os.path.join(os.getcwd(), "printer")
        os.makedirs(folder, exist_ok=True)

        receipt_path = os.path.join(folder, f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")

        img = Image.new('RGB', (600, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 18)
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()

        draw.text((50, 20), "Al-Khwarizmi Pharmacy", fill=(0, 0, 0), font=font_bold)
        draw.text((50, 50), "Baghdad University", fill=(0, 0, 0), font=font)
        draw.line((50, 80, 550, 80), fill=(0, 0, 0), width=2)

        y = 100
        for item in self.order_items:
            draw.text((50, y), f"{item['name']} x{item['quantity']}  -  ${item['subtotal']:.2f}", fill=(0, 0, 0), font=font)
            y += 30

        total = sum(i['subtotal'] for i in self.order_items)
        draw.line((50, y, 550, y), fill=(0, 0, 0), width=2)
        draw.text((50, y+10), f"Total: ${total:.2f}", fill=(0, 0, 0), font=font_bold)

        img.save(receipt_path)

        # Try to print
        try:
            os.startfile(receipt_path, "print")
            messagebox.showinfo("Printed", f"Receipt saved and sent to printer!\n{receipt_path}")
        except Exception as e:
            messagebox.showwarning("Print Failed", f"Saved but printing failed: {str(e)}")
