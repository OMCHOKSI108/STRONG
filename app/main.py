from fastapi import FastAPI, UploadFile, File, Form
from app.utils import load_from_file, load_from_url
from app.model import get_caption

app = FastAPI()

@app.post("/caption")
async def caption_image(image: UploadFile = File(None), url: str = Form(None)):
    if image:
        img = load_from_file(image.file)
    elif url:
        img = load_from_url(url)
    else:
        return {"error": "Provide image or URL"}
    caption = get_caption(img)
    return {"caption": caption}
