import ttkbootstrap as ttkb
from logintoapp import LoginWindow
from pharmacy_app import PharmacyApp

if __name__ == "__main__":
    app = ttkb.Window(themename="flatly")
    app.withdraw()

    login_window = LoginWindow(app)

    app.wait_window(login_window.root)

    if login_window.login_successful:
        app.deiconify()
        pharmacy_app = PharmacyApp(app)
        app.mainloop()
    else:
        app.destroy()
