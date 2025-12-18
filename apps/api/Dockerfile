# Qteria API - Production Dockerfile for Railway
# This Dockerfile ensures libmagic is available at runtime

FROM python:3.11-slim

# Install system dependencies
# libmagic1: Required by python-magic for MIME type detection
# libpq-dev: Required by psycopg2 for PostgreSQL connections
# gcc: Required for compiling some Python packages
# tesseract-ocr: Required for OCR support (pytesseract)
# tesseract-ocr-*: Language data packs for multi-language OCR support
# poppler-utils: Required for PDF to image conversion (pdf2image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libpq-dev \
    gcc \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway routes traffic to port 8000 (shown in Networking settings)
# Uvicorn must bind to 0.0.0.0 (not localhost) to accept external connections
# Note: Railway does NOT provide a PORT env var - port 8000 is hardcoded in Railway config
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
