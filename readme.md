# Image Captioning and Multilingual Assistive Tool

This project is a web-based application built with Flask, enabling users to upload images, generate captions, translate them into multiple Indian languages, and listen to the translated captions. It utilizes cutting-edge AI models for image captioning, translation, and speech synthesis.

---

## Link of the Site
[Image Captioning and Multilingual Assistive Tool](https://aiandml-project.onrender.com/)


## Few Screenshots of the Site



## Features

- **Image Captioning**: Automatically generates descriptive captions for uploaded images.
- **Multilingual Translation**: Translates captions into several Indian languages such as Hindi, Tamil, Kannada, Bengali, Marathi, and more.
- **Audio Narration**: Provides text-to-speech narration of the translated captions.
- **User-Friendly Interface**: Upload images and select target languages easily.

---



## Technologies Used

- Flask for web application development.
- PyTorch and Hugging Face Transformers for AI models.
- Google Text-to-Speech (gTTS) for audio narration.
- PIL (Pillow) for image processing.
- IndicTrans2 for multilingual translation.

---

## Supported Languages

- **Hindi**  
- **Telugu**  
- **Tamil**  
- **Bengali**  
- **Gujarati**  
- **Marathi**  
- **Kannada**  

---

## Requirements

- Python 3.8 or later.  
- GPU (optional) for faster model inference.  
- Libraries listed in the `requirements.txt` file.  

---

## How It Works

1. **Upload an Image**: Users upload an image through the web interface.
2. **Caption Generation**: The system generates a caption for the image.
3. **Translation**: The caption is translated into the selected Indian language.
4. **Audio Narration**: The translated text is synthesized into audio and provided for download or playback.

---

## Setup and Deployment

1. Clone the repository and navigate to the project directory.
2. Install dependencies using the `requirements.txt` file.
3. Ensure the necessary models are downloaded during the initialization phase.
4. Start the Flask server locally or deploy it on platforms like Render, AWS, or Heroku.
5. Access the application through a web browser at the provided URL.

---

## Deployment on Render

To deploy this project on Render:  

1. Upload the repository to a GitHub or GitLab account.
2. Link the repository to Render for deployment.
3. Add necessary environment variables and ensure models are downloaded at runtime.
4. Start the application and share the generated URL.

---

## Project Structure

- `app.py`: Main Flask application script.
- `templates/`: HTML templates for the web interface.
- `static/uploads/`: Directory for storing uploaded images and generated audio files.
- `IndicTrans2/`: IndicTrans2 library for multilingual translation.

---

## Challenges

1. Ensuring compatibility across diverse languages and scripts.
2. Optimizing inference time for translation and captioning models.
3. Managing model deployment for seamless web access.

---

## Future Enhancements

- Add support for more languages.
- Implement real-time audio playback.
- Improve UI design and responsiveness.

---

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

---

## Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/) for pre-trained models.
- [AI4Bharat IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) for multilingual translation.
- Google Text-to-Speech (gTTS) for speech synthesis.

---
