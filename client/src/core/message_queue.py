import queue

class MessageQueue:
    def __init__(self):
        self._q: queue.Queue = queue.Queue()
    
    def put(self, event: dict):
        self._q.put_nowait(event)
    
    def poll(self) -> list[dict]:
        events = []
        try:
            while True:
                events.append(self._q.get_nowait())
        except queue.Empty:
            pass

        return events