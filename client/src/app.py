import customtkinter as ctk

from comunicacao_redes.client.ui.login_window import LoginWindow

def main():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()