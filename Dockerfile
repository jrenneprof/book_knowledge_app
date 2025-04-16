# Use a lightweight and secure Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy dependency list first to leverage Docker layer caching
COPY requirements.txt .
# Use a slim Python image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (helps with Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables required by Cloud Run
ENV PORT=8080

# Expose the port the app will run on
EXPOSE 8080

# Start the app using Gunicorn, optimized for Cloud Run
CMD ["gunicorn", "main:app", "--bind=0.0.0.0:8080", "--workers=1", "--threads=8", "--timeout=0"]

