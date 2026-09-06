# ============================================================
# Weather Intelligence Platform — Dockerfile
# ============================================================
# Build:   docker build -t weather-intel .
# Run:     docker run -p 8000:8000 --env-file .env weather-intel
# ============================================================

FROM python:3.9-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements-docker.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Ensure HuggingFace / transformers models are cached offline
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1

# Expose FastAPI port
EXPOSE 8000

# Default: start FastAPI server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
