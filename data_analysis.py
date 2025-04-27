import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from database import Database
import threading
import tkinter as tk
from tkinter import messagebox
import sys
import os
import subprocess
import time
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MedicineAnalysis:
    def __init__(self, progress_callback=None, max_rows=100000):
        self.progress_callback = progress_callback
        self.max_rows = max_rows
        # Initialize DataFrames to avoid attribute errors
        self.orders_df = pd.DataFrame()
        self.order_items_df = pd.DataFrame()
        self.medicines_df = pd.DataFrame()
        self.employees_df = pd.DataFrame()
        self.sales_merged = pd.DataFrame()
        self.configure_plots()
        
    def configure_plots(self):
        sns.set(style="whitegrid", rc={"figure.figsize": (6, 4)})
        plt.rcParams['savefig.dpi'] = 80
        plt.rcParams['font.size'] = 8
    
    def update_progress(self, message):
        logger.info(message)
        if self.progress_callback:
            self.progress_callback(message)
    
    def load_data(self):
        start_time = time.time()
        self.update_progress("Loading data...")
        try:
            # Check dataset size with fallback
            order_count = 0
            order_item_count = 0
            try:
                order_count_result = Database.fetch_all("SELECT COUNT(*) FROM orders")
                order_item_count_result = Database.fetch_all("SELECT COUNT(*) FROM order_items")
                order_count = order_count_result[0][0] if order_count_result else 0
                order_item_count = order_item_count_result[0][0] if order_item_count_result else 0
                logger.info(f"Dataset size: {order_count} orders, {order_item_count} order items")
                if order_count > self.max_rows or order_item_count > self.max_rows:
                    self.update_progress(f"Warning: Dataset too large ({order_count} orders, {order_item_count} order items). Proceeding with limited data.")
            except Exception as db_error:
                error_msg = f"Failed to check dataset size: {str(db_error)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                self.update_progress(f"Warning: {error_msg}. Proceeding without size check.")

            # Limit to last 90 days
            cutoff_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
            orders_query = f"SELECT order_id, employee_id, order_date FROM orders WHERE order_date >= '{cutoff_date}'"
            order_items_query = "SELECT order_id, medicine_id, quantity, unit_price FROM order_items"
            medicines_query = "SELECT medicine_id, name, quantity FROM medicines"
            employees_query = "SELECT employee_id, name FROM employees"

            try:
                # Fetch data with individual try-except blocks for better debugging
                self.update_progress("Fetching orders...")
                orders = Database.fetch_all(orders_query)
                self.orders_df = pd.DataFrame(orders, columns=['order_id', 'employee_id', 'order_date'])
                
                self.update_progress("Fetching order items...")
                order_items = Database.fetch_all(order_items_query)
                self.order_items_df = pd.DataFrame(order_items, columns=['order_id', 'medicine_id', 'quantity', 'unit_price'])
                # Convert to numeric, coercing errors to NaN
                self.order_items_df['quantity'] = pd.to_numeric(self.order_items_df['quantity'], errors='coerce')
                self.order_items_df['unit_price'] = pd.to_numeric(self.order_items_df['unit_price'], errors='coerce')
                # Log data types for debugging
                logger.info(f"order_items_df dtypes:\n{self.order_items_df.dtypes}")
                # Calculate total_price, handling NaN values
                self.order_items_df['total_price'] = self.order_items_df['unit_price'] * self.order_items_df['quantity']
                # Replace NaN in total_price with 0
                self.order_items_df['total_price'] = self.order_items_df['total_price'].fillna(0)
                
                self.update_progress("Fetching medicines...")
                medicines = Database.fetch_all(medicines_query)
                self.medicines_df = pd.DataFrame(medicines, columns=['medicine_id', 'name', 'quantity'])
                self.medicines_df['quantity'] = pd.to_numeric(self.medicines_df['quantity'], errors='coerce')
                
                self.update_progress("Fetching employees...")
                employees = Database.fetch_all(employees_query)
                self.employees_df = pd.DataFrame(employees, columns=['employee_id', 'name'])
                
            except Exception as db_error:
                error_msg = f"Database query failed: {str(db_error)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                raise Exception(error_msg)

            # Cache merged data with explicit suffixes
            self.update_progress("Merging data...")
            self.sales_merged = (self.order_items_df
                                .merge(self.orders_df, on='order_id', how='inner')
                                .merge(self.medicines_df, on='medicine_id', how='inner', suffixes=('_sold', '_stock')))
            
            elapsed = time.time() - start_time
            self.update_progress(f"Data loaded in {elapsed:.2f}s")
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise Exception(error_msg)
    
    def analyze_top_medicines(self):
        start_time = time.time()
        self.update_progress("Analyzing top medicines...")
        try:
            if self.sales_merged.empty:
                self.update_progress("No sales data for top medicines")
                return None
                
            top_meds = (self.sales_merged
                       .groupby('name')['quantity_sold']
                       .sum()
                       .nlargest(10))
            
            if top_meds.empty:
                self.update_progress("No top medicines data")
                return None
                
            fig, ax = plt.subplots()
            top_meds.plot(kind='bar', ax=ax)
            ax.set_title('Top 10 Medicines')
            ax.set_xlabel('Medicine')
            ax.set_ylabel('Total Sold')
            plt.tight_layout()
            plt.savefig("top_medicines.png")
            plt.close()
            
            elapsed = time.time() - start_time
            self.update_progress(f"Top medicines analyzed in {elapsed:.2f}s")
            return fig
        except Exception as e:
            error_msg = f"Error in top medicines analysis: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def analyze_monthly_sales(self):
        start_time = time.time()
        self.update_progress("Analyzing monthly sales...")
        try:
            if self.orders_df.empty or self.order_items_df.empty:
                self.update_progress("No orders data for monthly sales")
                return None
                
            orders_df = self.orders_df.copy()
            orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
            orders_df['month'] = orders_df['order_date'].dt.to_period('M')
            
            monthly_sales = (self.order_items_df
                           .merge(orders_df[['order_id', 'month']], on='order_id', how='inner')
                           .groupby('month')['total_price']
                           .sum())
            
            # Debug log to inspect monthly_sales
            logger.info(f"Monthly sales data:\n{monthly_sales}")
            
            if monthly_sales.empty:
                self.update_progress("No monthly sales data")
                return None
                
            fig, ax = plt.subplots()
            monthly_sales.plot(kind='line', marker='o', ax=ax)
            ax.set_title('Monthly Sales')
            ax.set_ylabel('Revenue')
            ax.set_xlabel('Month')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("monthly_sales.png")
            plt.close()
            
            elapsed = time.time() - start_time
            self.update_progress(f"Monthly sales analyzed in {elapsed:.2f}s")
            return fig
        except Exception as e:
            error_msg = f"Error in monthly sales analysis: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def analyze_employee_performance(self):
        start_time = time.time()
        self.update_progress("Analyzing employee performance...")
        try:
            if self.order_items_df.empty or self.employees_df.empty:
                self.update_progress("No employee sales data")
                return None
                
            sales_by_emp = (self.order_items_df
                           .merge(self.orders_df[['order_id', 'employee_id']], on='order_id', how='inner')
                           .merge(self.employees_df, on='employee_id', how='inner')
                           .groupby('name')['total_price']
                           .sum()
                           .reset_index())
            
            if sales_by_emp.empty:
                self.update_progress("No employee performance data")
                return None
                
            fig, ax = plt.subplots()
            sns.barplot(data=sales_by_emp, x='name', y='total_price', ax=ax)
            ax.set_title('Employee Sales')
            ax.set_xlabel('Employee')
            ax.set_ylabel('Total Sales')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("employee_performance.png")
            plt.close()
            
            elapsed = time.time() - start_time
            self.update_progress(f"Employee performance analyzed in {elapsed:.2f}s")
            return fig
        except Exception as e:
            error_msg = f"Error in employee performance analysis: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def analyze_stock(self):
        start_time = time.time()
        self.update_progress("Analyzing stock levels...")
        try:
            if self.medicines_df.empty:
                return {'low_stock': "No medicine data", 'restock_recommendations': "No recommendations"}
                
            low_stock = self.medicines_df[self.medicines_df['quantity'] < 20][['name', 'quantity']]
            low_stock_str = low_stock.to_string(index=False) if not low_stock.empty else "No low stock medicines"
            
            last_30_days = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
            recent_orders_query = f"SELECT order_id FROM orders WHERE order_date >= '{last_30_days}'"
            recent_orders = pd.DataFrame(Database.fetch_all(recent_orders_query), columns=['order_id'])
            
            if recent_orders.empty:
                return {'low_stock': low_stock_str, 'restock_recommendations': "No recent sales data"}
                
            recent_sales = (self.order_items_df
                           .merge(recent_orders, on='order_id', how='inner')
                           .groupby('medicine_id')['quantity']
                           .sum() / 30)
            
            restock_df = (self.medicines_df[['medicine_id', 'name', 'quantity']]
                         .set_index('medicine_id')
                         .join(recent_sales.rename('avg_daily_sales')))
            
            restock_df['avg_daily_sales'] = restock_df['avg_daily_sales'].fillna(0)
            restock_df['days_left'] = restock_df['quantity'] / restock_df['avg_daily_sales'].replace(0, 1)
            restock_df['recommended_reorder'] = restock_df.apply(
                lambda row: max(0, int((30 * row['avg_daily_sales']) - row['quantity']))
                if row['days_left'] < 10 else 0, axis=1)
            
            restock_recs = restock_df[restock_df['recommended_reorder'] > 0][
                ['name', 'quantity', 'avg_daily_sales', 'recommended_reorder']]
            restock_str = restock_recs.to_string(index=False) if not restock_recs.empty else "No restock recommendations"
            
            elapsed = time.time() - start_time
            self.update_progress(f"Stock analyzed in {elapsed:.2f}s")
            return {'low_stock': low_stock_str, 'restock_recommendations': restock_str}
        except Exception as e:
            error_msg = f"Error in stock analysis: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def run_full_analysis(self):
        start_time = time.time()
        self.update_progress("Starting analysis...")
        try:
            self.load_data()
            results = {
                'plots': {
                    'top_medicines': self.analyze_top_medicines(),
                    'monthly_sales': self.analyze_monthly_sales(),
                    'employee_performance': self.analyze_employee_performance()
                },
                'stock_analysis': self.analyze_stock()
            }
            elapsed = time.time() - start_time
            self.update_progress(f"Analysis complete in {elapsed:.2f}s!")
            return results
        except Exception as e:
            error_msg = f"Error running full analysis: {str(e)}"
            self.update_progress(error_msg)
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise Exception(error_msg)

class AnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medicine Sales Analysis")
        self.root.geometry("1000x600")
        
        self.setup_ui()
        self.analysis = MedicineAnalysis(self.update_progress, max_rows=100000)
    
    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.main_frame, text="Pharmacy Sales Analysis", 
                font=('Arial', 16)).pack(pady=10)
        
        self.run_button = tk.Button(
            self.main_frame, 
            text="Run Full Analysis", 
            command=self.run_analysis_threaded,
            width=20)
        self.run_button.pack(pady=10)
        
        self.results_frame = tk.Frame(self.main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = tk.Label(self.main_frame, text="", fg='blue')
        self.status_label.pack(pady=5)
    
    def update_progress(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message, fg='blue'))
    
    def run_analysis_threaded(self):
        self.run_button.config(state=tk.DISABLED)
        self.status_label.config(text="Starting analysis...", fg='blue')
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        threading.Thread(target=self._run_analysis_background, daemon=True).start()
    
    def _run_analysis_background(self):
        try:
            results = self.analysis.run_full_analysis()
            self.root.after(0, lambda: self.show_results(results))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.show_error(error_msg))
        finally:
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
    
    def show_results(self, results):
        self.status_label.config(text="Analysis complete!", fg='green')
        
        tk.Label(self.results_frame, text="Medicines with Low Stock:", 
                font=('Arial', 12, 'bold')).pack(anchor='w', pady=(10, 5))
        
        low_stock_text = tk.Text(self.results_frame, height=5, width=80)
        low_stock_text.pack(fill=tk.X, padx=5)
        low_stock_text.insert(tk.END, results['stock_analysis']['low_stock'])
        low_stock_text.config(state=tk.DISABLED)
        
        tk.Label(self.results_frame, text="Restock Recommendations:", 
                font=('Arial', 12, 'bold')).pack(anchor='w', pady=(10, 5))
        
        restock_text = tk.Text(self.results_frame, height=5, width=80)
        restock_text.pack(fill=tk.X, padx=5)
        restock_text.insert(tk.END, results['stock_analysis']['restock_recommendations'])
        restock_text.config(state=tk.DISABLED)
        
        plot_frame = tk.Frame(self.results_frame)
        plot_frame.pack(pady=10)
        
        for plot_name, filename in [
            ("Top Medicines", "top_medicines.png"),
            ("Monthly Sales", "monthly_sales.png"),
            ("Employee Performance", "employee_performance.png")
        ]:
            if results['plots'][plot_name.replace(" ", "_").lower()]:
                tk.Button(plot_frame, text=f"View {plot_name}", 
                         command=lambda f=filename: self.show_plot(f)).pack(side=tk.LEFT, padx=5)
    
    def show_plot(self, filename):
        try:
            if os.path.exists(filename):
                if os.name == 'nt':
                    os.startfile(filename)
                else:
                    opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                    subprocess.call([opener, filename])
            else:
                messagebox.showerror("Error", f"Plot file {filename} not found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open plot: {str(e)}")
    
    def show_error(self, message):
        self.status_label.config(text=f"Error: {message}", fg='red')
        messagebox.showerror("Analysis Error", message)

# Entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = AnalysisApp(root)
    root.mainloop()