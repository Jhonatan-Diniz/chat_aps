import customtkinter as ctk
from tkinter import filedialog
from typing import Callable

from comunicacao_redes.client.core import config
from comunicacao_redes.client.utils.image_preview import check_size

class InputBar(ctk.CTkFrame):
    ACCEPTED_TYPES = [
        ("Imagens", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
        ("Documentos", "*.pdf *.txt *.docx *.xlsx"),
        ("Todos", "*.*"),
    ]

    def __init__(self, master, on_send: Callable[[str], None], on_attach: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_send = on_send
        self._on_attach = on_attach

        self._build_ui()
    
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)

        self._btn_attach = ctk.CTkButton(
            self,
            text="+",
            width=36,
            height=36,
            corner_radius=18,
            font=("", 18),
            fg_color="transparent",
            border_width=1,
            command=self._on_attach_click,
        )
        self._btn_attach.grid(row=0, column=0, padx=(8,4), pady=8)

        self._entry = ctk.CTkTextbox(
            self,
            height=36,
            wrap="word",
            activate_scrollbars=False
        )
        self._entry.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        self._entry.bind("<Return>", self._on_return)
        self._entry.bind("<Shift-Return>", self._on_shift_return)

        self._btn_send = ctk.CTkButton(
            self,
            text="Enviar",
            width=72,
            height=36,
            command=self._on_send_click,
        )
        self._btn_send.grid(row=0, column=2, padx=(4, 8), pady=8)

        self._lbl_error = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=("", 11),
            anchor="w",
        )
        self._lbl_error.grid(row=1, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 4))

    def _on_return(self, event):
        self._on_send_click()
        return "break"
    
    def _on_shift_return(self, event):
        return None
    
    def _on_send_click(self):
        content = self._entry.get("1.0", "end").strip()
        if not content:
            return
        self._entry.delete("1.0", "end")
        self._clear_error()
        self._on_send(content)
    
    def _on_attach_click(self):
        path = filedialog.askopenfilename(title="Selecionar arquivo", filetypes=self.ACCEPTED_TYPES)
        if not path:
            return
        
        if not check_size(path):
            self._show_error(f"Arquivo excede o limite de {config.max_upload_mb} MB.")
            return
        
        self._clear_error()
        self._on_attach(path)
    
    def _show_error(self, msg: str):
        self._lbl_error.configure(text=msg)
    
    def _clear_error(self):
        self._lbl_error.configure(text="")
    
    def set_enable(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._entry.configure(state=state)
        self._btn_send.configure(state=state)
        self._btn_attach.configure(state=state)