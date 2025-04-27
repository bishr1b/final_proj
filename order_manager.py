import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Order, Medicine, Customer, Employee, Database
from PIL import Image, ImageDraw, ImageFont
import os

class OrderManager:
    def __init__(self, parent_frame, on_order_saved=None):
        self.frame = ttk.Frame(parent_frame)
        self.current_order = None
        self.order_items = []
        self.on_order_saved = on_order_saved  # Callback to notify other components
        self.setup_ui()

    def setup_ui(self):
        # Main frames
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # Order info frame
        order_info_frame = ttk.LabelFrame(top_frame, text="Order Information", padding=10)
        order_info_frame.pack(side="left", fill="y", padx=5)
        
        ttk.Label(order_info_frame, text="Customer:").grid(row=0, column=0, sticky="e")
        self.customer_combo = ttk.Combobox(order_info_frame, state="readonly")
        self.customer_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(order_info_frame, text="Employee:").grid(row=1, column=0, sticky="e")
        self.employee_combo = ttk.Combobox(order_info_frame, state="readonly")
        self.employee_combo.grid(row=1, column=1, pady=5)
        
        ttk.Label(order_info_frame, text="Order Type:").grid(row=2, column=0, sticky="e")
        self.order_type_combo = ttk.Combobox(order_info_frame, 
                                         values=["Retail", "Wholesale", "Online"])
        self.order_type_combo.grid(row=2, column=1, pady=5)
        self.order_type_combo.current(0)
        
        # Add item frame
        add_item_frame = ttk.LabelFrame(top_frame, text="Add Item", padding=10)
        add_item_frame.pack(side="left", fill="y", padx=5)
        
        ttk.Label(add_item_frame, text="Medicine:").grid(row=0, column=0, sticky="e")
        self.medicine_combo = ttk.Combobox(add_item_frame, state="readonly")
        self.medicine_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(add_item_frame, text="Quantity:").grid(row=1, column=0, sticky="e")
        self.quantity_entry = ttk.Entry(add_item_frame)
        self.quantity_entry.grid(row=1, column=1, pady=5)
        
        ttk.Button(add_item_frame, text="Add Item", 
                 command=self.add_item).grid(row=2, column=1, pady=5)
        
        # Order items treeview
        items_frame = ttk.LabelFrame(self.frame, text="Order Items", padding=10)
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.items_tree = ttk.Treeview(items_frame, columns=(
            "Medicine", "Quantity", "Price", "Subtotal"
        ), show="headings")
        
        columns = [
            ("Medicine", "Medicine", 200),
            ("Quantity", "Qty", 80),
            ("Price", "Unit Price", 100),
            ("Subtotal", "Subtotal", 100)
        ]
        
        for col_id, col_text, width in columns:
            self.items_tree.heading(col_id, text=col_text)
            self.items_tree.column(col_id, width=width, anchor="center")
        
        self.items_tree.pack(fill="both", expand=True)
        
        # Total and buttons frame
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_label = ttk.Label(bottom_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=5)
        
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side="right")
        
        ttk.Button(button_frame, text="New Order", 
                 command=self.new_order).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save Order", 
                 command=self.save_order).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Generate Bill", 
                 command=self.generate_bill).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Item", 
                 command=self.delete_item).pack(side="left", padx=5)
        
        # Load initial data
        self.load_combos()
        self.new_order()

    def load_combos(self):
        try:
            # Load customers
            customers = Customer.get_all()
            self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]
            if customers:
                self.customer_combo.current(0)
            
            # Load employees
            employees = Employee.get_all()
            self.employee_combo['values'] = [f"{e['employee_id']} - {e['name']}" for e in employees]
            if employees:
                self.employee_combo.current(0)
            
            # Load medicines
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
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Get medicine details
            med = Medicine.get_by_id(medicine_id)
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            if quantity > med['quantity']:
                messagebox.showerror("Error", f"Only {med['quantity']} available in stock")
                return
            
            # Calculate price based on order type
            price = float(med['price'])
            if self.order_type_combo.get() == "Wholesale" and 'wholesale_price' in med:
                price = float(med['wholesale_price'])
            
            # Add to order items
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
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_items_tree(self):
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        
        total = 0.0
        for item in self.order_items:
            self.items_tree.insert("", "end", values=(
                item['name'],
                item['quantity'],
                f"${item['price']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total += item['subtotal']
        
        self.total_label.config(text=f"Total: ${total:.2f}")

    def delete_item(self):
        selected = self.items_tree.selection()
        if not selected:
            return
        
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
        order_type = self.order_type_combo.get()
        
        if not customer or not employee or not order_type:
            messagebox.showwarning("Warning", "Please fill all order information fields")
            return
        
        conn = None
        try:
            customer_id = int(customer.split(" - ")[0])
            employee_id = int(employee.split(" - ")[0])
            
            # Validate customer and employee existence
            if not Customer.get_by_id(customer_id):
                raise ValueError("Selected customer does not exist")
            if not Employee.get_by_id(employee_id):
                raise ValueError("Selected employee does not exist")
            
            order_data = {
                'customer_id': customer_id,
                'employee_id': employee_id,
                'order_type': order_type,
                'total_amount': sum(item['subtotal'] for item in self.order_items),
                'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Start a transaction
            conn = Database.get_connection()
            
            # Create the order and its items
            order_id = Order.create_with_details(order_data, self.order_items)
            if not order_id:
                raise ValueError("Order creation failed, no order ID returned")
            
            # Update medicine quantities
            for item in self.order_items:
                success = Medicine.reduce_stock(item['medicine_id'], item['quantity'])
                if not success:
                    raise RuntimeError(f"Failed to update stock for {item['name']}")
            
            # Update customer loyalty points
            points = int(order_data['total_amount'] * 10)
            success = Customer.add_loyalty_points(customer_id, points)
            if not success:
                raise RuntimeError("Failed to update customer loyalty points")
            
            # Commit the transaction
            conn.commit()
            
            messagebox.showinfo("Success", f"Order #{order_id} created successfully")
            self.new_order()
            
            # Notify other components (e.g., MedicineManager) to refresh
            if self.on_order_saved:
                self.on_order_saved()
            
        except ValueError as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Input Error", str(e))
        except RuntimeError as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
        finally:
            if conn:
                Database.close_connection(conn)

    def generate_bill(self):
        if not self.order_items:
            messagebox.showwarning("Warning", "No items in the order!")
            return
            
        customer_id = None
        customer_selection = self.customer_combo.get()
        if customer_selection:
            try:
                customer_id = int(customer_selection.split(" - ")[0])
            except (IndexError, ValueError):
                messagebox.showerror("Error", "Invalid customer selection")
                return

        bill_data = []
        for item in self.order_items:
            bill_data.append((
                item['name'],
                item['quantity'],
                float(item['price']),
                float(item['subtotal'])
            ))

        total_price = sum(item[3] for item in bill_data)
        self.generate_receipt_image(bill_data, total_price, customer_id)

    def generate_receipt_image(self, bill_data, total_price, customer_id=None):
        """Generate a receipt image file"""
        img = Image.new('RGB', (600, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
    
        try:
            font = ImageFont.truetype("arial.ttf", 18)
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
    
        # Pharmacy name and address
        draw.text((50, 20), "Al-Khwarizmi Pharmacy", fill=(0, 0, 0), font=font_bold)
        draw.text((50, 50), "Address: Baghdad University", fill=(0, 0, 0), font=font)
    
        # Current date
        current_date = datetime.now().strftime("%m/%d/%Y")
        draw.text((50, 80), f"Date: {current_date}", fill=(0, 0, 0), font=font)
    
        # Customer name (fetched using customer_id)
        customer_name = "Unknown"
        if customer_id:
            customer = Customer.get_by_id(customer_id)
            if customer:
                customer_name = customer['name']
        draw.text((50, 110), f"Customer name: {customer_name}", fill=(0, 0, 0), font=font)
    
        # Manager name
        draw.text((50, 140), "Manager: Ahmed Ayad Mezher", fill=(0, 0, 0), font=font)
    
        # Divider line
        draw.line((50, 170, 550, 170), fill=(0, 0, 0), width=2)
    
        # Bill details header
        draw.text((50, 180), "Description", fill=(0, 0, 0), font=font_bold)
        draw.text((400, 180), "Price", fill=(0, 0, 0), font=font_bold)
    
        # Add bill details
        y_offset = 210
        for medicine, quantity, price, total in bill_data:
            draw.text((50, y_offset), f"{medicine} (x{quantity})", fill=(0, 0, 0), font=font)
            draw.text((400, y_offset), f"${total:.2f}", fill=(0, 0, 0), font=font)
            y_offset += 30
    
        # Divider line
        draw.line((50, y_offset, 550, y_offset), fill=(0, 0, 0), width=2)
    
        # Tax calculation (assuming 10% tax)
        tax = total_price * 0.10
        draw.text((50, y_offset + 10), "Tax (10%)", fill=(0, 0, 0), font=font)
        draw.text((400, y_offset + 10), f"${tax:.2f}", fill=(0, 0, 0), font=font)
    
        # Total price
        draw.text((50, y_offset + 40), "TOTAL", fill=(0, 0, 0), font=font_bold)
        draw.text((400, y_offset + 40), f"${total_price + tax:.2f}", fill=(0, 0, 0), font=font_bold)
    
        # Divider line
        draw.line((50, y_offset + 70, 550, y_offset + 70), fill=(0, 0, 0), width=2)
    
        # Thank you message
        draw.text((50, y_offset + 90), "THANK YOU!", fill=(0, 0, 0), font=font_bold)
    
        # Stars divider
        draw.text((50, y_offset + 120), "*" * 50, fill=(0, 0, 0), font=font)
    
        # Fake QR code placeholder
        for x in range(252, 355, 6):
            draw.line((x, y_offset + 170, x, y_offset + 230), fill=(0, 0, 0), width=2)
        draw.text((240, y_offset + 240), "  8743518769", fill=(0, 0, 0), font=font)
    
        # Save the image
        receipt_path = os.path.join(os.getcwd(), "receipt.png")
        img.save(receipt_path)
        messagebox.showinfo("Receipt Saved", f"Receipt saved as {receipt_path}")