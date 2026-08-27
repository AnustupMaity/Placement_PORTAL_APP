FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies (build tools for psycopg2, xhtml2pdf fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application files
COPY . /app

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set working directory to app root
ENV PYTHONPATH=/app/backend

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
