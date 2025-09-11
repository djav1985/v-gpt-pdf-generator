# syntax=docker/dockerfile:1.4

FROM python:3.10-slim as builder

WORKDIR /app

# Install build tools for Python packages that may need compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    pkg-config \
    libffi-dev \
    libxml2-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into venv – build cache will reuse this layer
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install -r requirements.txt

# ---- Final stage ----
FROM python:3.10-slim

WORKDIR /app

# Install system libs required by WeasyPrint & friends
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libffi-dev \
    libxml2-dev \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/venv /app/venv
COPY ./app /app

EXPOSE 8888

ENV WORKERS=2
ENV UVICORN_CONCURRENCY=32
ENV PATH="/app/venv/bin:$PATH"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8888 --workers $WORKERS --limit-concurrency $UVICORN_CONCURRENCY"]
