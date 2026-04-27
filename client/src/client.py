import socket
import threading


class Client:
    def __init__(self, host, port, on_message):
        self.host = host
        self.port = port
        self.on_message = on_message
        self.socket = None
        self.running = False
    
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        self.running = True

        threading.Thread(target=self.listen, daemon=True).start()
    
    def send(self, message: str):
        try:
            payload = message.encode("utf-8")
            frame = encode_frame(payload)

            self.socket.sendall(frame)
        except Exception as e:
            print("ERRO ao enviar: ", e)
    
    def listen(self):
        while self.running:
            try:
                data = self.socket.recv(4096)

                if not data:
                    break

                frame = decode_frame(data)
                message = frame["payload"].decode("utf-8")

                self.on_message(message)
            except Exception as e:
                print("ERRO ao receber: ", e)
                break
        self.disconnect()
    
    def disconnect(self):
        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

