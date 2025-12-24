# Use Python 3.11 Slim as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (Heavy!)
# build-essential: for compiling python packages
# tesseract-ocr: for Image OCR
# libmagic1: for file type detection
# poppler-utils: for PDF processing
# libreoffice: for DOCX/XLSX conversion
# ffmpeg: for Audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libmagic1 \
    poppler-utils \
    libreoffice \
    ffmpeg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch (Lightweight, ~200MB instead of 2GB)
# This prevents timeouts and corruption on slow networks
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
COPY requirements.txt .
RUN sed -i 's/python-magic-bin/python-magic/g' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/incoming data/sorted data/database

# Expose port
EXPOSE 5000

# Start command
CMD ["python", "app.py"]
