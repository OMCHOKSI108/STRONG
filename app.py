from flask import Flask, render_template, request, redirect, url_for, flash
from transformers import BlipProcessor, BlipForConditionalGeneration
from diffusers import StableDiffusionPipeline
from PIL import Image
import requests
import torch
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "ai_webapp_secret_key"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== Load Models Once ==========
try:
    # Text to Image
    sd_pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4",  # More reliable model
        torch_dtype=torch.float16
    ).to("cuda")

    # Image to Text
    blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")
except Exception as e:
    print(f"Error loading models: {str(e)}")

# ---- Text to Image Route ----
@app.route("/text-to-image", methods=["GET", "POST"])
def text_to_image():
    if request.method == "POST":
        prompt = request.form.get("prompt")
        if not prompt:
            flash("Please enter a text prompt", "error")
            return redirect(url_for("text_to_image"))
        
        try:
            image = sd_pipe(prompt).images[0]
            filename = f"generated_{secure_filename(prompt[:20])}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            return render_template("text_to_image.html", 
                                image_path=f"uploads/{filename}",
                                prompt=prompt)
        except Exception as e:
            flash(f"Error generating image: {str(e)}", "error")
            return redirect(url_for("text_to_image"))
    
    return render_template("text_to_image.html")

# ---- Image to Text Route ----
@app.route("/image-to-text", methods=["GET", "POST"])
def image_to_text():
    if request.method == "POST":
        image = None
        image_path = None

        # Handle file upload
        if "image_file" in request.files and request.files["image_file"].filename:
            file = request.files["image_file"]
            if not allowed_file(file.filename):
                flash("Only image files (png, jpg, jpeg, gif, webp) are allowed", "error")
                return redirect(url_for("image_to_text"))
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image = Image.open(filepath).convert("RGB")
            image_path = f"uploads/{filename}"

        # Handle URL input
        elif request.form.get("image_url"):
            try:
                img_url = request.form.get("image_url")
                response = requests.get(img_url, stream=True)
                if response.status_code != 200:
                    flash("Failed to download image from URL", "error")
                    return redirect(url_for("image_to_text"))
                
                image = Image.open(response.raw).convert("RGB")
                filename = f"from_url_{secure_filename(img_url.split('/')[-1])}"
                if '.' not in filename:
                    filename += '.jpg'
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                image_path = f"uploads/{filename}"
            except Exception as e:
                flash(f"Error processing image URL: {str(e)}", "error")
                return redirect(url_for("image_to_text"))
        else:
            flash("Please upload an image or provide an image URL", "error")
            return redirect(url_for("image_to_text"))

        try:
            inputs = blip_processor(image, "A photograph of", return_tensors="pt").to("cuda")
            out = blip_model.generate(**inputs)
            description = blip_processor.decode(out[0], skip_special_tokens=True)
            return render_template("image_to_text.html", 
                                description=description,
                                image_path=image_path)
        except Exception as e:
            flash(f"Error generating description: {str(e)}", "error")
            return render_template("image_to_text.html", image_path=image_path)

    return render_template("image_to_text.html")

# ---- Home Page ----
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)