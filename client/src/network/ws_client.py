import json
import threading

from comunicacao_redes.client.core.message_queue import MessageQueue


class WebsocketClient:
    def __init__(self, host: str, port: int, msg_queue: MessageQueue):
        self._host = host
        self._port = port
        self._queue = msg_queue
        self._ws: ClientConnection | None = None
        self._running = False
        self._send_lock = threading.Lock()
    
    def connenct(self):
        uri = f"ws://{self._host}:{self.port}"
        self._ws = connect(uri)

    def start_reading(self):
        self._running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        try:
            while self._running:
                raw = self._ws.recv()
                
                try:
                    msg = json.loads(raw)
                    self._queue.put(msg)
                except json.JSONDecodeError:
                    pass            
        except connectionClosed:
            pass
        finally:
            self._queue.put({"type": "disconnected"})
    
    def send_json(self, data: dict):
        payload = json.dumps(data)
        with self._send_lock:
            self._ws.send(payload)
    
    def send_login(self, username: str, password: str) -> str:
        self.send_json({
            "type": "auth",
            "action": "login",
            "username": username,
            "password": password
        })

        return self._expect_tolken()
    
    def send_register(self, username: str, password: str) -> str:
        self.send_json({
            "type": "auth",
            "action": "register",
            "username": username,
            "password": password
        })

        return self._expect_tolken()
    
    def send_message(self, to: str, content: str, media_url: str = None):
        self.send_json({
            "type": "message",
            "to": to,
            "content": content,
            "media_url": media_url
        })
    
    def request_history(self, contact: str, since_ts: float = 0):
        self.send_json({
            "type": "history_rec",
            "contact": contact,
            "since": since_ts
        })
    
    def disconnect(self):
        self._running == False
        try:
            self._ws.close()
        except Exception:
            pass

     
    def _expect_token(self) -> str:
        raw = self._ws.recv()
        response = json.loads(raw)
        if response.get("status") == "ok":
            return response["token"]
        raise AuthError(response.get("message: ", "Autenticação falhou."))
       
class AuthError(Exception):
    pass