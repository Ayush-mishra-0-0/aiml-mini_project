from flask import Flask, request, render_template, send_file, jsonify
import os
import sys
from PIL import Image
import torch
from transformers import (
    VisionEncoderDecoderModel, 
    ViTImageProcessor, 
    GPT2TokenizerFast,
    AutoModelForSeq2SeqLM, 
    AutoTokenizer
)
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = Path('static/uploads')
MODELS_CACHE = Path('models_cache')  # Add local cache directory
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
MODELS_CACHE.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

# Global variables
device = "cuda" if torch.cuda.is_available() else "cpu"
models = {}

def load_model_with_retry(model_name, model_class, **kwargs):
    """Load model with retry logic and detailed error handling"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Loading model {model_name} (Attempt {attempt + 1}/{max_retries})")
            
            # Set cache directory
            kwargs['cache_dir'] = str(MODELS_CACHE)
            
            # Add offline mode handling
            if os.path.exists(str(MODELS_CACHE / model_name)):
                kwargs['local_files_only'] = True
                logger.info(f"Using cached model from {MODELS_CACHE / model_name}")
            
            model = model_class.from_pretrained(model_name, **kwargs)
            logger.info(f"Successfully loaded model {model_name}")
            return model
            
        except OSError as e:
            logger.error(f"OSError loading model {model_name}: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"Failed to load model {model_name} after {max_retries} attempts")
            continue
            
        except Exception as e:
            logger.error(f"Unexpected error loading model {model_name}: {str(e)}")
            raise

def initialize_models():
    """Initialize all required models with enhanced error handling"""
    try:
        # Image captioning models
        logger.info("Loading image captioning models...")
        models['caption_model'] = load_model_with_retry(
            "nlpconnect/vit-gpt2-image-captioning",
            VisionEncoderDecoderModel,
            trust_remote_code=True
        ).to(device)
        
        models['caption_tokenizer'] = load_model_with_retry(
            "nlpconnect/vit-gpt2-image-captioning",
            GPT2TokenizerFast
        )
        
        models['image_processor'] = load_model_with_retry(
            "nlpconnect/vit-gpt2-image-captioning",
            ViTImageProcessor
        )

        # Translation models
        logger.info("Loading translation models...")
        en_indic_ckpt_dir = "ai4bharat/indictrans2-en-indic-1B"
        
        models['trans_tokenizer'] = load_model_with_retry(
            en_indic_ckpt_dir,
            AutoTokenizer,
            trust_remote_code=True
        )
        
        models['trans_model'] = load_model_with_retry(
            en_indic_ckpt_dir,
            AutoModelForSeq2SeqLM,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        if device == "cuda":
            models['trans_model'] = models['trans_model'].half()
        models['trans_model'] = models['trans_model'].to(device)
        models['trans_model'].eval()

        logger.info("All models loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Critical error during model initialization: {str(e)}")
        return False




@app.route('/health', methods=['GET'])
def health_check():
    """Add a health check endpoint to verify model loading status"""
    try:
        if not models.get('image_processor'):
            return jsonify({
                'status': 'error',
                'message': 'Image processor not initialized'
            }), 503
            
        return jsonify({
            'status': 'healthy',
            'models_loaded': list(models.keys())
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize models before starting the server
    if not initialize_models():
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)