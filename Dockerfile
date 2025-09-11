# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# Install build tools for any packages that might need compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    pkg-config \
    libffi-dev \
    libxml2-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and cache
COPY /cache /app/cache
COPY requirements.txt /app

# Create venv and install deps (prefer cache, fall back to PyPI)
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir --find-links /app/cache -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

# System libs required by WeasyPrint and friends
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libffi-dev \
    libxml2-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder
COPY --from=builder /app/venv /app/venv

# Copy your application
COPY ./app /app

EXPOSE 8888

ENV WORKERS=2
ENV UVICORN_CONCURRENCY=32
ENV PATH="/app/venv/bin:$PATH"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8888 --workers $WORKERS --limit-concurrency $UVICORN_CONCURRENCY"]
