# AI Web App: Text-to-Image & Image-to-Text Generator

A Flask web application that harnesses the power of Hugging Face's AI models to provide:
1. Text-to-Image generation using Stable Diffusion
2. Image-to-Text captioning with powerful vision-language models

## Features

### Text-to-Image Generation
- Enter descriptive text prompts
- Generate high-quality images based on those prompts
- Download the generated images

### Image-to-Text Captioning
- Upload images or provide image URLs
- Generate detailed, human-like captions
- Support for multiple image formats (PNG, JPG, JPEG, GIF, WEBP)

## Technologies Used

- **Frontend:** HTML5, CSS3 (custom layout)
- **Backend:** Flask (Python)
- **AI Models:**
  - `runwayml/stable-diffusion-v1-5` for image generation
  - `microsoft/git-large-coco` for image captioning
- **API:** Hugging Face Inference API

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Hugging Face account with API access token

### Installation

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd ai-web-app
   ```

2. **Create a virtual environment**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

5. **Set up your Hugging Face API token**
   - Copy the `.env.example` file to `.env`
   - Replace `hf_your_token_here` with your actual Hugging Face API token
   ```
   cp .env.example .env
   ```

6. **Create the uploads directory**
   ```
   mkdir -p static/uploads
   ```

### Running the Application

1. **Start the Flask server**
   ```
   flask run
   ```

2. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`

## Deployment Options

This application can be deployed on various platforms:

- **Render.com**: Easy deployment with built-in Python support
- **Hugging Face Spaces**: Direct integration with Hugging Face
- **Heroku**: Classic cloud platform with free and paid tiers
- **PythonAnywhere**: Python-focused hosting service

## Getting a Hugging Face API Token

1. Create an account on [Hugging Face](https://huggingface.co/)
2. Go to your profile and navigate to Settings > Access Tokens
3. Create a new token with 'read' access

## Tips for Better Results

### Text-to-Image Generation
- Be specific and detailed in your descriptions
- Include artistic styles (e.g., "oil painting", "digital art", "photorealistic")
- Mention lighting, perspective, and composition
- Use adjectives to describe colors, textures, and mood

### Image-to-Text Captioning
- Use clear, high-quality images for better descriptions
- Images with clear subjects and contexts work best
- The model works with both photographs and artwork

## License

This project is licensed under the MIT License - see the LICENSE file for details.