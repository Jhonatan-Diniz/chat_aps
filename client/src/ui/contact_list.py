import customtkinter as ctk
from typing import Callable

class ContactList(ctk.CTkFrame):
    def __init__(self, master, on_select: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)
        self._on_select = on_select
        self._contacts: dict[str, "_ContactItem"] = {}
        self._selected: str | None = None

        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Conversas",
            font=("", 13, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        self._scroll = ctk.CTkScrollableFrame(self, label_text="")
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self._scroll.grid_columnconfigure(0, weight=1)
    
    def add_contact(self, username: str):
        if username in self._contacts:
            return
        
        item = _ContactItem(
            self._scroll,
            username=username,
            on_click=self._on_item_click,
        )
        item.grid(row=len(self._contacts), column=0, sticky="ew", padx=4, pady=2)
        self._contacts[username] = item
    
    def mark_unread(self, username: str):
        if username in self._contacts:
            self._contacts[username].set_unread(True)
    
    def clear_unread(self, username: str):
        if username in self._contacts:
            self._contacts[username].set_unread(False)
    
    def set_selected(self, username: str):
        if self._selected and self._selected in self._contacts:
            self._contacts[self._selected].set_selected(False)
        self._selected = username
        if username in self._self._contacts:
            self._contacts[username].set._selected(True)
    
    def _on_item_click(self, username: str):
        self._set_selected(username)
        self._on_select(username)

class _ContactItem(ctk.CTkFrame):
    COLOR_NORMAL = "transparent"
    COLOR_SELECTED = ("gray75", "gray30")
    COLOR_UNREAD = ("gray85", "gray25")
    def __init__(self, master, username: str, on_click: Callable[[str], None],  **kwargs):
        super().__init__(master, fg_color=self.COLOR_NORMAL, **kwargs)
        self._username = username
        self._on_click = on_click
        self._unread = False
        self._selected = False

        self._build_ui()
        self.bind("<Button-1>", self._click)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        self._avatar = ctk.CTkLabel(
            self,
            text=self._username[0].upper(),
            width=36,
            height=36,
            corner_radius=18,
            fg_color=("gray70", "gray40"),
            font=("", 14, "bold"),
        )
        self._avatar.grid(row=0, column=0, rowspan=2, padx=(8, 0), pady=6, sticky="w")
        self._avatar.bind("<Button-1>", self._click)

        self._lbl_name = ctk.CTkLabel(
            self,
            text=self._username,
            anchor="w",
            font=("", 13),
        )
        self._lbl_name.grid(row=0, column=1, sticky="ew", padx=(8, 4), pady=(6, 0))
        self._lbl_name.bind("<Button-1>", self._click)

        self._badge = ctk.CTkLabel(
            self,
            text="",
            width=18,
            height=18,
            corner_radius=9,
            fg_color=("gray50", "gray60"),
            font=("", 11, "bold"),
            text_color="white"
        )
    
    def set_selected(self, selected: bool):
        self._selected = selected
        self._refresh_color()
    
    def set_unread(self, unread: bool):
        self._unread = unread
        if unread:
            self._badge.configure(text="!")
            self._badge.grid(row=0, column=2, rowspan=2, padx=(0, 8), pady=6)
        else:
            self._badge.configure(text="")
            self._badge.grid_remove()
        self._refresh_color()
    
    def _refresh_color(self):
        if self._selected:
            color = self.COLOR_SELECTED
        elif self._unread:
            color = self.COLOR_UNREAD
        else:
            color = self.COLOR_NORMAL
        self.configure(fg_color=color)
    
    def _click(self, _event=None):
        self._on_click(self._username)