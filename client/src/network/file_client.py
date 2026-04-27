import json
import os
import queue
import threading

import urllib

class FileClient:
    def __init__(self, server_url: str, session_token: str, progress_queue: queue.Queue):
        self.server_url = server_url
        self.session_token = session_token
        self.progress_queue = progress_queue
    
    def upload_asyn(self, path: str, msg_id: str):
        t = threading.Thread(
            target = self._upload(),
            args = (path, msg_id),
            daemon = True
        )
        t.start()
    
    def _upload(self, path: str, msg_id: str):
        try:
            media_url = self._multipart_post(path, msg_id)
            self.progress_queue().put({
                "type": "upload_done",
                "msg_id": msg_id,
                "media_url": media_url
            })
        except Exception as e:
            self.progress_queue.put({
                "type": "upload_error",
                "msg_id": msg_id,
                "error": str(e)
            })
    
    def _multipart_post(self, path: str, msg_id: str) -> str:
        boundry = "----ChatBoundary" + msg_id
        fname = os.path.basename()
        total_size = os.path.getsize(path)

        header = (
            f"--{boundry}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
            f"Content-type: application/octed-stream\r\n\r\n"
        ).encode()
        fotter = f"\r\n--{boundry}--\r\n".encode()

        body = bytearray()
        body += header

        sent = 0
        CHUNK = 64 * 1024
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                body += chunk
                sent += len(chunk)
                progress = sent / total_size
                self.progress_queue.put({
                    "type": "upload_progress",
                    "msg_id": msg_id,
                    "progress": progress
                })
        body += fotter

        req = urllib.request.Request(
            f"{self.server_url}/upload",
            data = bytes(body),
            method = "POST",
            headers = {
                "Content-type": f"multipart/form-data; boundry={boundry}",
                "Authorization": f"Bearer {self.session_token}"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result["media_url"]
    
    