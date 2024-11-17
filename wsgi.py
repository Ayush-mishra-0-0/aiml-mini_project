from app import app, initialize_models
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize models when the WSGI app starts
if not initialize_models():
    logger.error("Failed to initialize models. Starting anyway but expect errors.")

if __name__ == "__main__":
    app.run()