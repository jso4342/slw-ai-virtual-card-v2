# Dockerfile for Google Cloud Run Deployment
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffer output
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure data & temp directories exist with proper write permissions
RUN mkdir -p /app/data /tmp && chmod -R 777 /app/data /tmp

# Expose port
EXPOSE 8080

# Run uvicorn server with explicit PORT fallback
CMD exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
