# Build stage
FROM python:3.10-slim AS builder
ARG REPO_URL
LABEL org.opencontainers.image.source="${REPO_URL}"

# Set the working directory
WORKDIR /app

# Copy the requirements file and cache
COPY requirements.txt /app

# Install Python dependencies in a virtual environment
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install -r requirements.txt

# Final stage
FROM python:3.10-slim
ARG REPO_URL
LABEL org.opencontainers.image.source="${REPO_URL}"

# Set the working directory
WORKDIR /app

# Install system dependencies for WeasyPrint and related libraries
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage (only necessary parts)
COPY --from=builder /app/venv/lib/python3.10/site-packages /app/venv/lib/python3.10/site-packages

# Copy the rest of the application
COPY ./app /app

# Expose port 8888 to the outside world
EXPOSE 8888

# Define environment variables
ENV WORKERS=2
ENV UVICORN_CONCURRENCY=32
ENV PATH="/app/venv/bin:$PATH"

# Set the command to run your FastAPI application with Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8888 --workers $WORKERS --limit-concurrency $UVICORN_CONCURRENCY"]

