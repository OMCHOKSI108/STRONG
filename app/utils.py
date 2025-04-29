from PIL import Image
import requests
from io import BytesIO

def load_from_file(file):
    return Image.open(file).convert("RGB")

def load_from_url(url: str):
    r = requests.get(url)
    return Image.open(BytesIO(r.content)).convert("RGB")
