
import customtkinter as ctk

from comunicacao_redes.client.core import config
from comunicacao_redes.client.core.auth import AuthSession
from comunicacao_redes.client.core.local_cash import LocalCache
from comunicacao_redes.client.core.message_queue import MessageQueue
from comunicacao_redes.client.network.file_client import FileClient
from comunicacao_redes.client.network.ws_client import WebsocketClient
from comunicacao_redes.client.ui.contact_list import ContactList
from comunicacao_redes.client.ui.input_bar import InputBar
from comunicacao_redes.client.ui.message_area import MessageArea
from comunicacao_redes.client.ui.message_bubble import MessageBubble
from comunicacao_redes.client.utils.notifications import NotificationManager


class ChatWindow(ctk.CTkToplevel):
    POLL_MS = 50

    def __init__(self, ws_client: WebsocketClient, session: AuthSession, msg_queue: MessageQueue):
        super().__init__()
        self.title("Chat Redes")
        self.geometry("1280x720")
        self.minsize("960x480")

        self._ws = ws_client
        self._session = session
        self._queue = msg_queue
        self._cache = LocalCache()
        self._files = FileClient(
            server_url=config.server_url,
            session_token=session.token,
            progress_queue=msg_queue
        )
        self._notifi = NotificationManager()
        self._contact: str|None = None
        self._bubbles: dict[str, "MessageBubble"] = {}

        self._input_bar.set_enable(False)
        
        # self.configure(fg_color=['gray92', 'gray14'])
        # self.msg_queue = MessageQueue()

        # self.client = None
        # self.criar_layout()

        # self._bubbles: dict[str, MessageBubble] = {}
        self._build_ui()
        self._load_contacts()
        self._after_poll()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # def criar_layout(self):
    #     self.sidebar = self.criar_sidebar()
    #     self.chat_area = self.criar_chat_area()

    # def criar_sidebar(self):
    #     frame = CTkScrollableFrame(self, width=250, corner_radius=0)
    #     frame.pack(side="left", fill="y")

    #     self.criar_contato(frame, "Jhonatan", "192.168.0.16")

    #     return frame
    
    # def criar_contato(self, parent, nome, ip):
    #     contato = CTkFrame(parent, height=80)
    #     contato.pack(fill="x", padx=5, pady=5)
    #     contato.pack_propagate(False)

    #     CTkLabel(contato, text=nome, font=CTkFont(size=18)).pack(expand=True)
    #     CTkLabel(contato, text=ip).pack()
    
    # def criar_chat_area(self):
    #     frame = CTkFrame(self)
    #     frame.pack(side="right", expand=True, fill="both")

    #     self.header = self.criar_header(frame)
    #     self.mensagens = self.criar_area_mensagens(frame)
    #     self._input_area = self.criar_input(frame)

    #     return frame
    
    # def criar_header(self, parent):
    #     frame =CTkFrame(parent, height=80)
    #     frame.pack(fill="x")
    #     frame.pack_propagate(False)

    #     CTkLabel(frame, text="Yáskara", font=CTkFont(size=20)).pack(side="left", padx=10)
    #     CTkLabel(frame, text="192.168.0.11").pack(side="left")

    #     return frame
    
    # def criar_area_mensagens(self, parent):
    #     frame = CTkScrollableFrame(parent, corner_radius=0)
    #     frame.pack(expand=True, fill="both")

    #     return frame
    
    # def criar_input(self, parent):
    #     frame = CTkFrame(parent, height=80)
    #     frame.pack(fill="x")
    #     frame.pack_propagate(False)

    #     self.input_text = CTkTextbox(frame)
    #     self.input_text.pack(side="left", expand=True, fill="both", padx=5, pady=5)
    #     self.input_text.bind("<Return>", lambda e: self.enviar_mensagem())
    #     CTkButton(frame, text="Enviar", command=self.enviar_mensagem).pack(side="right", padx=5)

    #     return frame
    
    # def criar_mensagem(self, texto, lado="esquerda"):
    #     container = CTkFrame(self.mensagens)
    #     container.pack(fill="x", pady=5)

    #     balao = CTkFrame(container)
    #     balao.pack(side="left" if lado == "esquerda" else "right", padx=10)

    #     CTkLabel(balao, text=texto, wraplength=400, justify="left").pack(padx=10, pady=5)
    
    # def enviar_mensagem(self):
    #     texto = self.input_text.get("0.0", "end").strip()

    #     if texto:
    #         self.criar_mensagem(texto, lado="direita")
    #         self.input_text.delete("0.0", "end")
    
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._contact_list = ContactList(
            self,
            on_select=self._on_contact_selected,
            width=220
        )
        self._contact_list.grid(row=0, column=0, sticky="nsew")

        right = ctk.CTkFrame(self)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._message_area = MessageArea(right, session=self._session)
        self._message_area.grid(row=0, column=0, sticky="nsew")

        self._input_bar = InputBar(
            right,
            on_send=self._on_send_text,
            on_attach=self._on_attach
        )
        self._input_bar.grid(row=1, column=0, sticky="ew")

        self._header = ctk.CTkLabel(
            right,
            text="Selecione um contato",
            font=("", 15, "bold"),
            anchor="w"
        )
        self._header.grid(row=0, column=0, sticky="new", padx=16, pady=(12, 0))
    
    def _load_contacts(self):
        contacts = self._cache.get_contacts(self._session.username)
        for contact in contacts:
            self._contact_list.add_contact(contact)

    def _after_poll(self):
        for event in self.msg_queue.poll():
            self._handle_event(event)
        
        self.after(self.POLL_MS, self._after_poll)
    
    def _handle_event(self, event: dict):
        event_type = event["type"]

        if event_type == "message":
            self._on_incoming_message(event)

        elif event_type == "history_res":
            self._on_history_respone(event)

        elif event_type == "read_recipt":
            self._cache.update_status(event["msg_id"], "read")
            bubble = self._bubbles.get(event["msg_id"])
            if bubble:
                bubble.update_status("read")

        elif event_type == "upload_progress":
            bubble = self._bubbles.get(event["msg_id"])
            if bubble:
                bubble.update_progress(event["progress"])

        elif event_type == "upload_done":
            bubble = self._bubbles.get(event["msg_id"])
            if bubble:
                bubble.update_progress(1.0)
            self.ws_client.send_message(
                to=self.current_contact,
                content="",
                media_url=event["media_url"],
            )

        elif event_type == "upload_error":
            bubble = self._bubbles.get(event["msg_id"])
            if bubble:
                bubble.show_error("Falha no Envio do Arquivo.")

        elif event_type == "disconected":
            self._on_disconected()

    def _on_incoming_message(self, msg: dict):
        self._cache().save(msg)

        sender = msg["from"]

        self._contact_list.add_contact(sender)

        if sender == self._contact:
            bubble = self._message_area.append(msg, is_mine=False)
            self._bubbles[msg["id"]] = bubble
            self._ws.send_json({
                "type": "read_receipt",
                "msg_id": msg["id"],
            })
        else:
            self._notifi.notifi(
                title=sender,
                message=msg.get("content") or "Arquivo Recebido"
            )
            self._contact_list.mark_unread(sender)
    def _on_history_response(self, event: dict):
        messages = event.get("messages", [])
        for msg in messages:
            self._cache.save(msg)
        
        self._render_conversation()
    
    def _on_contact_selected(self, contact: str):
        self._input_bar.set_enable(True)
        self._contact = contact
        self._header.configure(text=contact)
        self._contact_list.clear_unread(contact)
        self._render_conversation()

        since = self._cache.last_timestamp(self._session.username, contact)
        self._ws.request_history(contact=contact, since_ts=since)
    
    def _render_conversation(self):
        self._message_area.clear()
        self._bubbles.clear()

        if not self._contact:
            return
        
        messages = self._cache.get_conversation(
            me=self._session.username,
            contact=self._contact
        )
        for msg in messages:
            is_mine = msg["from"] == self._session.username
            bubble = self._message_area.append(msg, is_mine=is_mine)
            self._bubbles[msg["id"]] = bubble
    
    def _on_send_text(self, content: str):
        if not self._contact or not content.strip():
            return
        
        import uuid, time
        msg = {
            "id": str(uuid.uuid4()),
            "from": self._session.username,
            "to": self._contact,
            "content": content,
            "media_url": None,
            "timestamp": time.time(),
            "status": "sent"
        }
        self._cache.save(msg)
        bubble = self._message_area().append(msg, is_mine=True)
        self._bubbles[msg["id"]] = bubble

        self._ws.send_message(
            to=self._contact,
            content=content
        )
    
    def _on_attach(self, path: str):
        if not self._contact:
            return
        
        import uuid, time
        from comunicacao_redes.client.utils.image_preview import make_thumbnail

        msg_id = str(uuid.uuid4())
        preview = make_thumbnail(path)

        msg = {
            "id": msg_id,
            "from": self._session.username,
            "to": self._contact,
            "content": None,
            "media_url": None,
            "filename": __import__("os").path.basename(path),
            "timestamp": time.time(),
            "status": "sent",
            "_preview_image": preview,
        }
        self._cache.save(msg)
        bubble = self._message_area().append(msg, is_mine=True)
        self._bubbles[msg["id"]] = bubble

        self._files.upload_asyn(path, msg["id"])
    
    def _on_disconnected(self):
        self._input_bar.set_enable(False)
        self._header.configure(text="Desconectado - Reconectando...")
    
    def _on_close(self):
        self._ws.disconnect()
        self._cache.close()
        self.destroy()