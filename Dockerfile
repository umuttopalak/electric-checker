# Use the official Python image as a base image
FROM python:3.12.7-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=wsgi.py
ENV PYTHONPATH=/app

# Expose port
EXPOSE 3003

# Run the application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:3003", "wsgi:app"]

# Copy Swagger specs
COPY app/swagger_specs /app/app/swagger_specs
