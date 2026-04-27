import customtkinter as ctk
import io, os
from PIL import Image

TUMB_SIZE = (200, 200)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bnp"}
MAX_UPLOAD_MB = 20 * 1024 * 1024

def is_image(path: str) ->bool:
    return os.path.splitext(path)[1].lower() in IMAGE_EXTS

def check_size(path: str) ->bool:
    return os.path.getsize(path) <= MAX_UPLOAD_MB

def make_thumbnail(path: str) -> "ctk.CTkImage | None":
    if not is_image(path):
        return None

    try:
        img = Image.open(path).copy()
        img.thumbnail(TUMB_SIZE, IMAGE_EXTS.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
    except Exception:
        return None

