# AgriSaathi AI - Production Dockerfile
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr and writing pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

WORKDIR /app

# Install system dependencies (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Ensure data, logs, and upload directories exist
RUN mkdir -p /app/data/uploads /app/data/backups /app/logs

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/?health=true || exit 1

# Launch AgriSaathi AI Streamlit Application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]

