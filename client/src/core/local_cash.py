import sqlite3
import json
import os
from comunicacao_redes.client.core import config


class LocalCache:
    def __init__(self):
        db_path = config.local_cache_db
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = __import__("threading").Lock()
        self._init_schema()
    
    def _init_schema(self):
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id          TEXT PRIMARY KEY,
                    from_user   TEXT NOT NULL,
                    to_user     TEXT NOT NULL,
                    content     TEXT,
                    media_url   TEXT,
                    filename    TEXT,
                    timestamp   REAL NOT NULL,
                    status      TEXT NOT NULL DEFAULT 'sent',
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation
                ON messages (from_user, to_user, timestamp)
            """)
    
    def save(self, msg: dict):
        with self._lock:
            with self._conn:
                self._conn.execute("""
                    INSERT OR REPLACE INTO messages (id, from_user, to_user, content, media_url, filename, timestamp, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg["id"],
                    msg["from"],
                    msg["to"],
                    msg.get("content"),
                    msg.get("media_url"),
                    msg.get("file_name"),
                    msg["timestamp"],
                    msg.get("status", "sent")
                ))
    
    def update_status(self, msg_id: str, status: str):
        with self._lock:
            with self._conn:
                self._conn.execute(
                    "UPDATE messages SET status = ? WHERE id = ?",
                    (status, msg_id)
                )

    def get_conversation(self, me: str, contact: str, limit: int = 100) -> list[dict]:
        rows = None
        with self._lock:
            cur = self._conn.execute("""
                SELECT id, from_user, to_user, content, media_url, filename, timestamp, status
                FROM messages
                WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """, (me, contact, contact, me, limit))

            rows = cur.fetchall()

        return [self._row_to_dict(r) for r in reversed(rows)]
    
    def last_timestamp(self, me: str, contact: str):
        result = None
        with self._lock:
            cur = self._conn.execute("""
                SELECT MAX(timestamp) FROM messages
                WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
            """, (me, contact, contact, me))
            result = cur.fetchone()[0]

        return result or 0.0
    
    def get_contacts(self, me: str) -> list[str]:
        with self._lock:
            cur = self._conn.execute("""
                SELECT CASE
                    WHEN from_user = ? THEN to_user
                    ELSE from_user
                AND AS contact,
                MAX(timestamp) AS last_ts
                FROM messages
                WHERE from_user = ? OR to_user = ?
                GROUP BY contact
                ORDER BY last_ts DESC
            """, (me, me , me))
            return [row[0] for row in cur.fetchall()]
    
    def _row_to_dict(self, row: tuple) -> dict:
        keys = ("id", "from", "to", "content", "media_url", "filename", "timestamp", "status")
        return dict(zip(keys, row))
    
    def close(self):
        self._conn.close()