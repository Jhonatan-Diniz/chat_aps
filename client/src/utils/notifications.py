import sys
import threading


class NotificationManager:
    def __init__(self):
        self._backend = self._detect_backend()
    
    def _detect_backend(self) -> str:
        if sys.platform == "linux":
            return "notify_send"
        elif sys.plataform == "darwin":
            return "osascript"
        else:
            try:
                import win10toast
                return "win10toast"
            except ImportError:
                return "win_ctypes"
            
    
    def notify(self, title: str, message: str):
        threading.Thread(
            target=self._dispatch,
            args=(title, message),
            daemon=True,
        ).start()
    
    def _dispatch(self, title: str, message: str):
        try:
            if self._backend == "win10toast":
                self._notify_win10toast(title, message)
            elif self._backend == "win_ctypes":
                self._notify_win_ctypes(title, message)
            elif self._backend == "osascript":
                self._notify_osascript(title, message)
            else:
                self._notify_send(title, message)
        except Exception:
            pass
    
    # def _notify_win10toast(self, title: str, message: str):
    #     from win10toast import ToastNotifier
    #     ToastNotifier().show_toast(
    #         title,
    #         message,
    #         duration=4,
    #         threaded=True,
    #     )
    def _notify_win_ctypes(self, title: str, message: str):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)

    def _notify_osascript(self, title: str, message: str):
        import subprocess
        script = (
            f'display notification "{self._esc(message)}"'
            f'with title "{self._esc(title)}"'
        )
        subprocess.run(
            ["osascript", "-e", script],
            check=False,
            capture_output=True
        )

    def _notify_send(self, title: str, message: str):
        import subprocess
        subprocess.run(
            ["notify-send", "--expire-time=4000", title, message],
            check=False,
            capture_output=True,
        )
    
    def _esc(text: str) -> str:
        return text.replace('"', '\\"').replace("'", "\\'")