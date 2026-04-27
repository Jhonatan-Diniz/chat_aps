import customtkinter as ctk
from datetime import datetime


class MessageBubble(ctk.CTkFrame):
    MAX_WIDTH = 320
    def __init__(self, master, message: dict, is_mine: bool, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._message = message
        self._is_mine = is_mine
        self._build_ui()

    # def _build_ui(self):

    #     align = "e" if is_mine else "w"

    #     if self.message.get("media_url"):
    #         self._show_file_bubble(is_mine)
    #     else:
    #         ctk.CTkLabel(self, text=self.message["content"], wraplength=280).pack(anchor=align, padx=8, pady=4)
    
    # def _show_file_bubble(self, is_mine: bool):
    #     media_url = self.message["media_url"]
    #     fname = self.message.get("filename", "arquivo")
    #     preview = self.message.get("_preview_image")

    #     if preview:
    #         label = ctk.CTkLabel(self, image=preview, text="")
    #         label.pack(padx=6, pady=4)
    #         label.bind("<Button-1>", lambda e: self._open_file(media_url))
    #     else:
    #         ctk.CTkLabel(self, text=f"[arquivo] {fname}").pack(padx=6, pady=4)
        
    #     self.progress = ctk.CTkProgressBar(self, width=200)
    #     self.progress.set(0)
    #     self.progress.pack(padx=6, pady=(0, 4))

    def _build_ui(self):
        anchor = "e" if self._is_mine else "w"
        color = ("gray75", "gray25") if self._is_mine else ("gray85", "gray35")

        self._bubble = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=16,
        )
        self._bubble.pack(anchor=anchor, padx=8, pady=2)

        if self._message.get("_preview_image"):
            self._build_image()
        elif self._message.get("media_url") or self._message.get("filename"):
            self._build_file()
        else:
            self._build_text()
        
        self._build_footer()

        if self._message.get("filename") and not self._message.get("media_url"):
            self._build_progress()
    
    def _build_text(self):
        ctk.CTkLabel(
            self._bubble,
            text=self._message.get("content", ""),
            wraplength=self.MAX_WIDTH,
            justify="left",
            anchor="w",
        ).pack(padx=12, pady=(8, 4))

    def _build_image(self):
        preview = self._message["_preview_image"]
        lbl = ctk.CTkLabel(self._bubble, image=preview, text="")
        lbl.pack(padx=6, pady=6)
        lbl.bind("<Button-1>", lambda e: self._open_file(self._message.get("media_url")))

    def _build_file(self):
        fname = self._message.get("filename", "arquivo")
        frame = ctk.CTkFrame(self._bubble, fg_color="transparent")
        frame.pack(padx=10, pady=6)

        ctk.CTkLabel(
            frame,
            text="[ ]",
            font=("", 20),
            width=36,
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkLabel(
            frame,
            text=fname,
            anchor="w",
            wraplength=220,
        ).grid(row=0, column=1, sticky="w")

        if self._message.get("media_url"):
            frame.bind("<Button-1>", lambda e: self._open_file(self._message["media_url"]))

    def _build_footer(self):
        ts = self._message.get("timestamp", 0)
        hour = datetime.fromtimestamp(ts).strftime("%H:%M")
        text = hour

        if self._is_mine:
            status_icon = {"sent": "·", "delivered": "✓", "read": "✓✓"}
            text += " " + status_icon.get(self._message.get("statud", "sent"), "·")
        
        self._lbl_footer = ctk.CTkLabel(
            self._bubble,
            text=text,font=("", 11),
            text_color=("gray50", "gray60"),
            anchor="e",
        )
        self._lbl_footer.pack(padx=10, pady=(0, 6), anchor="e")
    
    def _build_progress(self):
        self._progress = ctk.CTkProgressBar(self._bubble, width=200)
        self._progress.set(0)
        self._progress.pack(padx=10, pady=(0, 6))
   
    def update_progress(self, value: float):
        if hasattr(self, "progress"):
            self.progress.set(value)
            if value >= 1.0:
                self.progress.pack_forget()
    
    def update_status(self, status: str):
        if not self._is_mine:
            return
        
        ts = self._message.get("timestamp", 0)
        hour = datetime.fromtimestamp(ts).strftime("%H:%M")
        icons = {"sent": "·", "delivered": "✓", "read": "✓✓"}
        self._lbl_footer.configure(text=hour + " " + icons.get(status, "·"))
    
    def show_error(self, message: str):
        ctk.CTkLabel(
            self._bubble,
            text=message,
            text_color="red",
            font=("", 11),
        ).pack(padx=10, pady=(0, 6))

    def _open_file(self, url: str):
        if url:
            import webbrowser
            webbrowser.open(url)
    
       