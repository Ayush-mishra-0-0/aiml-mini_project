# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clone required repositories
RUN git clone https://github.com/AI4Bharat/IndicTrans2.git && \
    git clone https://github.com/VarunGumma/IndicTransToolkit.git

# Install IndicTransToolkit
WORKDIR /app/IndicTransToolkit
RUN pip install --no-cache-dir -e .
WORKDIR /app

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt')"

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p static/uploads

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]