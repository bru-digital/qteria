# Qteria API - Production Dockerfile for Railway
# This Dockerfile ensures libmagic is available at runtime

FROM python:3.11-slim

# Install system dependencies
# libmagic1: Required by python-magic for MIME type detection
# libpq-dev: Required by psycopg2 for PostgreSQL connections
# gcc: Required for compiling some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway provides PORT environment variable dynamically
# Uvicorn must bind to 0.0.0.0 (not localhost) to accept external connections
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
