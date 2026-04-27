import threading

import customtkinter as ctk

from comunicacao_redes.client.core import config
from comunicacao_redes.client.core.auth import AuthSession
from comunicacao_redes.client.core.message_queue import MessageQueue
from comunicacao_redes.client.network.ws_client import AuthError, WebsocketClient
from comunicacao_redes.client.ui.chat_window import ChatWindow

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat Redes Login")
        self.geometry("1280x720")
        self.resizable(False, False)

        self._section = AuthSession()
        self._msg_queue = MessageQueue
        self._ws = None

        self._build_ui()
        self._entry_username.focus()
    
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Chat", font=("", 28, "bold")).grid(row=0, column=0, pady=(48, 4))
        ctk.CTkLabel(self, text="Entre com sua conta ou cadastre.", text_color="gray").grid(row=1, column=0, pady=(0, 32))

        self._entry_username = ctk.CTkEntry(self, placeholder_text="Usuario", width=260)
        self._entry_username.grid(row=2, column=0, pady=6)
        
        self._entry_password = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=260)
        self._entry_password.grid(row=3, column=0, pady=6)
        self._entry_password.bind("<Return>", lambda e: self._on_login())

        self._lbl_error = ctk.CTkLabel(self, text="", text_color="red")
        self._lbl_error.grid(row=4, column=0, pady=(16, 6))

        self._btn_login = ctk.CTkButton(self, text="Entrar", width=260, command=self._on_login)
        self._btn_login.grid(row=5, column=0, pady=(16, 6))

        ctk.CTkButton(
            self,
            text="Criar conta",
            width=260,
            fg_color="transparent",
            border_width=1,
            command=self._on_register
        ).grid(row=6, column=0, pady=6)

        self._spinner = ctk.CTkProgressBar(self, mode="indeterminate", width=260)
    
    def _on_login(self):
        self._submit(register=False)
    
    def _on_register(self):
        self._submit(register=True)
    
    def _submit(self, register: bool):
        username = self._entry_username.get().strip()
        password = self._entry_password.get()

        if not username or password:
            self._show_error("Preencha o usuário e senha")
            return
        if len(password) < 6:
            self._show_error("Senha deve ter ao menos 6 caracteres")
        
        self.set_load(True)

        threading.thread(
            target = self._auth_thread,
            args = (username, password, register),
            daemon = True
        ).start()

    def _auth_thread(self, username: str, password: str, register: bool):
        try:
            ws = WebsocketClient(
                host = config.server_host,
                port = config.server_port,
                msg_queue = self._msg_queue,
            )
            ws.connenct()

            if register:
                token = ws.send_register(username, password)
            else:
                token = ws.send_login(username, password)
            
            ws.start_reading()

            self.after(0, self._on_auth_sucess, ws, username, token)

        except AuthError as e:
            self.after(0, self.on_auth_failure, str(e))
        
        except ConnectionError:
            self.after(0, self.on_auth_failure("Não foi possível conectar ao servidor"))

    def _on_auth_sucess(self, ws: WebsocketClient, username: str, token: str):
        self._section.set(username=username, token=token)
        self._set_loading(False)

        chat = ChatWindow(
            ws_client=ws,
            section=self._section,
            msg_queue=self._msg_queue
        )
        self.withdraw()
        chat.protocol("WM_DELETE_WINDOW", lambda: self._on_chat_close(chat))
        chat.mainloop()
    
    def _on_auth_failure(self, message: str):
        self._set_loading(False)
        self._show_error(message)
    
    def _on_chat_close(self, chat: "ChatWindow"):
        chat.destroy()
        self.destroy()
    
    def _set_loading(self, loading: bool):
        if loading:
            self._btn_login.configure(state="disabled", text="Aguarde...")
            self._spinner.grid(row=7, column=0, pady=8)
            self._spinner.start()
            self._lbl_error.configure(text="")
        else:
            self._btn_login.configure(state="normal", text="Entrar")
            self._spinner.stop()
            self._spinner.grid_remove()
    
    def _show_error(self, msg: str):
        self._lbl_error.configure(text=msg)