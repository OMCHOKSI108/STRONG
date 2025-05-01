from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import requests
import base64
from werkzeug.utils import secure_filename
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
app.secret_key = "ai_webapp_secret_key"  # For flash messages
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------------------------------------------
# IMPORTANT: Replace with your Hugging Face API token or use .env file
# -------------------------------------------------------
# Get API token from environment variable or use the placeholder
# To use an environment variable, create a .env file with:
# HUGGINGFACE_API_TOKEN=your_actual_token_here
# -------------------------------------------------------
API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "hf_your_token_here")

# If you're not using a .env file, replace "hf_your_token_here" above with your actual token
# Example: API_TOKEN = "hf_AbCdEfGhIjKlMnOpQrStUvWxYz123456789"

# Setup headers for API requests
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# -------------------------------------------------------
# Models used in this application (no need to change these)
# -------------------------------------------------------
TEXT_TO_IMAGE_MODEL = "runwayml/stable-diffusion-v1-5"  # Text-to-image generation model
IMAGE_TO_TEXT_MODEL = "microsoft/git-large-coco"        # Image captioning model

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the homepage with options for both features"""
    return render_template('index.html')

@app.route('/text-to-image')
def text_to_image_page():
    """Render the text-to-image generation page"""
    return render_template('text_to_image.html')

@app.route('/image-to-text')
def image_to_text_page():
    """Render the image-to-text captioning page"""
    return render_template('image_to_text.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """Handle text-to-image generation requests"""
    prompt = request.form.get('prompt', '')
    
    if not prompt:
        flash('Please enter a text prompt', 'error')
        return redirect(url_for('text_to_image_page'))
    
    try:
        # Call the Hugging Face API for text-to-image generation
        api_url = f"https://api-inference.huggingface.co/models/{TEXT_TO_IMAGE_MODEL}"
        
        # Check if API token is set
        if API_TOKEN == "hf_your_token_here":
            flash('Please configure your Hugging Face API token', 'error')
            return redirect(url_for('text_to_image_page'))
        
        response = requests.post(
            api_url,
            headers=HEADERS,
            json={"inputs": prompt}
        )
        
        # Handle API errors
        if response.status_code == 401 or response.status_code == 403:
            flash('Authentication error. Please check your Hugging Face API token', 'error')
            return redirect(url_for('text_to_image_page'))
        elif response.status_code != 200:
            flash(f'Error from API: {response.status_code} - {response.text}', 'error')
            return redirect(url_for('text_to_image_page'))
        
        # Save the generated image
        image_bytes = response.content
        image_filename = f"generated_{secure_filename(prompt[:20])}.png"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        # Return the template with the image path
        return render_template(
            'text_to_image.html', 
            prompt=prompt, 
            image_path=f"uploads/{image_filename}"
        )
    
    except requests.exceptions.ConnectionError:
        flash('Network error. Please check your internet connection', 'error')
        return redirect(url_for('text_to_image_page'))
    except Exception as e:
        flash(f'Error generating image: {str(e)}', 'error')
        return redirect(url_for('text_to_image_page'))

@app.route('/generate-caption', methods=['POST'])
def generate_caption():
    """Handle image-to-text captioning requests"""
    caption = None
    image_path = None
    image_bytes = None
    
    # Check if API token is set
    if API_TOKEN == "hf_your_token_here":
        flash('Please configure your Hugging Face API token', 'error')
        return redirect(url_for('image_to_text_page'))
    
    # Check if request is for file upload or URL
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        
        if not allowed_file(file.filename):
            flash('Only image files (png, jpg, jpeg, gif, webp) are allowed', 'error')
            return redirect(url_for('image_to_text_page'))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_path = f"uploads/{filename}"
        
        # Prepare image for API
        with open(filepath, "rb") as image_file:
            image_bytes = image_file.read()
    
    elif request.form.get('image_url'):
        image_url = request.form.get('image_url')
        try:
            # Download image from URL
            response = requests.get(image_url)
            if response.status_code != 200:
                flash('Failed to download image from URL', 'error')
                return redirect(url_for('image_to_text_page'))
            
            # Save the image
            image_bytes = response.content
            
            # Extract a reasonable filename from the URL
            url_filename = image_url.split('/')[-1].split('?')[0]  # Remove query parameters
            if not url_filename or '.' not in url_filename:
                url_filename = 'from_url.jpg'  # Default name if none detected
            
            image_filename = f"url_{secure_filename(url_filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            image_path = f"uploads/{image_filename}"
        
        except requests.exceptions.ConnectionError:
            flash('Network error. Please check your internet connection or the image URL', 'error')
            return redirect(url_for('image_to_text_page'))
        except Exception as e:
            flash(f'Error processing image URL: {str(e)}', 'error')
            return redirect(url_for('image_to_text_page'))
    
    else:
        flash('Please upload an image or provide an image URL', 'error')
        return redirect(url_for('image_to_text_page'))
    
    try:
        # Call the Hugging Face API for image-to-text captioning
        api_url = f"https://api-inference.huggingface.co/models/{IMAGE_TO_TEXT_MODEL}"
        response = requests.post(
            api_url,
            headers=HEADERS,
            data=image_bytes
        )
        
        # Handle API errors
        if response.status_code == 401 or response.status_code == 403:
            flash('Authentication error. Please check your Hugging Face API token', 'error')
            return render_template('image_to_text.html', image_path=image_path)
        elif response.status_code != 200:
            flash(f'Error from API: {response.status_code} - {response.text}', 'error')
            return render_template('image_to_text.html', image_path=image_path)
        
        # Parse the response to get the caption
        result = response.json()
        
        if isinstance(result, list) and result:
            caption = result[0]['generated_text']
        else:
            caption = "No caption could be generated for this image."
        
        return render_template('image_to_text.html', image_path=image_path, caption=caption)
    
    except requests.exceptions.ConnectionError:
        flash('Network error when contacting Hugging Face API', 'error')
        return render_template('image_to_text.html', image_path=image_path)
    except Exception as e:
        flash(f'Error generating caption: {str(e)}', 'error')
        return render_template('image_to_text.html', image_path=image_path)

if __name__ == '__main__':
    # Check if API token is configured
    if API_TOKEN == "hf_your_token_here":
        print("⚠️  WARNING: Hugging Face API token not set!")
        print("Please set your API token by creating a .env file with HUGGINGFACE_API_TOKEN=your_token")
        print("Or edit the app.py file directly to set API_TOKEN to your actual token.")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0')