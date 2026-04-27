import customtkinter as ctk
from comunicacao_redes.client.core.auth import AuthSession
from comunicacao_redes.client.ui.message_bubble import MessageBubble

class MessageArea(ctk.CTkFrame):
    def __init__(self, master, session: AuthSession, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._session = session

        self._build_ui()
    
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            label_text=""
        )
        self._scroll.grid(row=0, column=0, sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)
    
    def append(self, msg: dict, is_mine: bool) -> MessageBubble:
        row = len(self._scroll.winfo_children())

        bubble = MessageBubble(self._scroll, msg=msg, is_mine=is_mine)

        bubble.grid(row=row, column=0, sticky="ew", padx=12, pady=2)
        self._scroll_to_bottom()
        return bubble
    
    def clear(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()
    
    def _scroll_to_bottom(self):
        self.after(0, self._scroll._parent_canvas.yview_moveto, 1.0)