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
from gtts import gTTS

# Add IndicTrans2 to Python path
indictrans_path = os.path.join(os.getcwd(), "IndicTrans2", "huggingface_interface")
if indictrans_path not in sys.path:
    sys.path.append(indictrans_path)

from IndicTransToolkit import IndicProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables
device = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 4
models = {}

def initialize_models():
    """Initialize all required models"""
    try:
        logger.info("Loading image captioning models...")
        models['caption_model'] = VisionEncoderDecoderModel.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        ).to(device)
        models['caption_tokenizer'] = GPT2TokenizerFast.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )
        models['image_processor'] = ViTImageProcessor.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )

        logger.info("Loading translation models...")
        en_indic_ckpt_dir = "ai4bharat/indictrans2-en-indic-1B"
        models['trans_tokenizer'] = AutoTokenizer.from_pretrained(
            en_indic_ckpt_dir, 
            trust_remote_code=True
        )
        models['trans_model'] = AutoModelForSeq2SeqLM.from_pretrained(
            en_indic_ckpt_dir,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        if device == "cuda":
            models['trans_model'] = models['trans_model'].half()
        models['trans_model'] = models['trans_model'].to(device)
        models['trans_model'].eval()

        logger.info("Initializing IndicProcessor...")
        models['ip'] = IndicProcessor(inference=True)

        logger.info("All models loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        return False

def generate_caption(image_path):
    """Generate caption for an image"""
    try:
        image = Image.open(image_path)
        img = models['image_processor'](image, return_tensors="pt").to(device)
        output = models['caption_model'].generate(**img)
        caption = models['caption_tokenizer'].batch_decode(
            output, 
            skip_special_tokens=True
        )[0]
        return caption
    except Exception as e:
        logger.error(f"Error generating caption: {str(e)}")
        raise

def translate_text(text, tgt_lang):
    """Translate text to target language"""
    try:
        src_lang = "eng_Latn"
        batch = models['ip'].preprocess_batch(
            [text], 
            src_lang=src_lang, 
            tgt_lang=tgt_lang
        )
        
        inputs = models['trans_tokenizer'](
            batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(device)
        
        with torch.no_grad():
            generated_tokens = models['trans_model'].generate(
                **inputs,
                use_cache=True,
                min_length=0,
                max_length=256,
                num_beams=5,
                num_return_sequences=1,
            )
        
        with models['trans_tokenizer'].as_target_tokenizer():
            translations = models['trans_tokenizer'].batch_decode(
                generated_tokens.detach().cpu().tolist(),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
        
        translated_text = models['ip'].postprocess_batch(
            translations, 
            lang=tgt_lang
        )[0]
        return translated_text
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise

# Language mapping
LANGUAGE_MAPPING = {
    'hindi': ('hin_Deva', 'hi'),
    'telugu': ('tel_Telu', 'te'),
    'tamil': ('tam_Taml', 'ta'),
    'bengali': ('ben_Beng', 'bn'),
    'gujarati': ('guj_Gujr', 'gu'),
    'marathi': ('mar_Deva', 'mr'),
    'kannada': ('kan_Knda', 'kn')
}

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', languages=LANGUAGE_MAPPING.keys())

@app.route('/process', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'})
        
        image = request.files['image']
        language = request.form.get('language', 'hindi')
        
        if image.filename == '':
            return jsonify({'error': 'No image selected'})
        
        # Save and process image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)
        
        # Generate caption
        caption = generate_caption(image_path)
        
        # Translate caption
        trans_lang, speech_lang = LANGUAGE_MAPPING[language]
        translation = translate_text(caption, trans_lang)
        print(f"Caption: {caption}, Translation: {translation}")
        # Generate audio
        tts = gTTS(text=translation, lang=speech_lang)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'speech.mp3')
        tts.save(audio_path)
        
        return jsonify({
            'caption': caption,
            'translation': translation,
            'image_path': image_path,
            'audio_path': audio_path
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Initialize models before starting the server
    if not initialize_models():
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)