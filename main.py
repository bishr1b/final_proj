import ttkbootstrap as ttkb
import json
import os

from logintoapp import LoginWindow
from pharmacy_app import PharmacyApp

class MainApp:
    def __init__(self):
        self.config_file = "config.json"
        self.style_name = self.load_theme()

        self.app = ttkb.Window(themename=self.style_name)
        self.app.withdraw()  # Hide main window at first

        self.login_window = LoginWindow(self.app)
        self.app.wait_window(self.login_window.root)

        if self.login_window.login_successful:
            self.app.deiconify()
            self.pharmacy_app = PharmacyApp(self.app, self)  # Pass self to PharmacyApp
            self.app.mainloop()
        else:
            self.app.destroy()

    def load_theme(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    return data.get("theme", "flatly")
            except Exception:
                return "flatly"
        return "flatly"

    def save_theme(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump({"theme": self.style_name}, f)
        except Exception:
            pass

if __name__ == "__main__":
    MainApp()
