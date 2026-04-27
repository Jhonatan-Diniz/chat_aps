from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    server_host: str = "localhost"
    server_port: int = 8080
    server_url: str = "http://localhost:8080"
    max_upload_mb: int = 20
    poll_interval: int = 50
    local_cache_db: str = "cache.db"

config = Config()