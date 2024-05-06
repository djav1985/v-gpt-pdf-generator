# Use a slimmer Python image as base
FROM python:3.9-slim as base

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file
COPY ./app/requirements.txt /app/

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./app /app

# Expose port 8060 to the outside world
EXPOSE 8050

# Define environment variables
ENV WORKERS=1
ENV UVICORN_CONCURRENCY=16

# Set the command to run your FastAPI application with Uvicorn and environment variables
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8050 --workers $WORKERS --limit-concurrency $UVICORN_CONCURRENCY"]