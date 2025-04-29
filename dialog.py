import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk

class CommonDialog(ttkb.Toplevel):
    def __init__(self, parent, title, fields, initial_data=None, align_right_labels=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x500")
        self.resizable(False, False)
        self.result = None

        self.fields = fields
        self.entries = {}

        container = ttkb.Frame(self)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttkb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        label_anchor = "e" if align_right_labels else "w"

        for i, (label, field_key, required, is_combobox, combobox_values) in enumerate(self.fields):
            lbl = ttkb.Label(self.scrollable_frame, text=label + (" *" if required else ""), font=("Helvetica", 10))
            lbl.grid(row=i, column=0, sticky="e", padx=(5, 10), pady=5)

            if is_combobox:
                entry = ttkb.Combobox(self.scrollable_frame, state="readonly", font=("Helvetica", 10))
                if combobox_values:
                    entry['values'] = combobox_values
                if initial_data and initial_data.get(field_key):
                    entry.set(initial_data[field_key])
            else:
                entry = ttkb.Entry(self.scrollable_frame, font=("Helvetica", 10))
                if initial_data and initial_data.get(field_key) is not None:
                    entry.insert(0, str(initial_data[field_key]))

            entry.grid(row=i, column=1, sticky="w", padx=(0, 5), pady=5)
            self.entries[field_key] = entry

        self.scrollable_frame.columnconfigure(0, weight=0)
        self.scrollable_frame.columnconfigure(1, weight=1)

        # Buttons Frame
        btn_frame = ttkb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=(10, 10))

        save_btn = ttkb.Button(btn_frame, text="💾 Save", command=self.on_save, bootstyle="success", width=10)
        save_btn.pack(side=LEFT, padx=5)

        cancel_btn = ttkb.Button(btn_frame, text="❌ Cancel", command=self.destroy, bootstyle="danger", width=10)
        cancel_btn.pack(side=LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def on_save(self):
        try:
            self.result = {
                field_key: (entry.get() if not isinstance(entry, ttkb.Combobox) else entry.get())
                for field_key, entry in self.entries.items()
            }
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {str(e)}")
