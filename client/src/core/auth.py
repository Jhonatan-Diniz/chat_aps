from dataclasses import dataclass, field

@dataclass
class AuthSession:
    username: str = ""
    token: str = ""

    def set(self, username: str, token: str):
        self.username = username
        self.token = token
    
    def clear(self):
        self.username = ""
        self.token = ""
    
    def is_authenticated(self) -> bool:
        return bool(self.token)