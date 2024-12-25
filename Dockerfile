# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install mysqlclient

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONPATH=/app

# Expose port
EXPOSE 3000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

# Copy Swagger specs
COPY app/swagger_specs /app/app/swagger_specs
