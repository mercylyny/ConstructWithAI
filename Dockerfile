# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Prevent Python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system dependencies (Poppler for PDF processing, Tesseract for OCR, and OpenCV dependencies)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Render expects
EXPOSE 10000

# Start the application with 2 workers to handle concurrent requests
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "2"]
