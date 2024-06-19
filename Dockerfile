# Build stage
FROM python:3.10-slim as builder

# Set the working directory
WORKDIR /app

# Copy the requirements file and cache
COPY /cache /app/cache
COPY requirements.txt /app

# Install Python dependencies in a virtual environment
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-index --find-links /app/cache -r requirements.txt

# Final stage
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for WeasyPrint and related libraries
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /app/venv /app/venv

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
