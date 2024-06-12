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

# Copy the virtual environment from the builder stage
COPY --from=builder /app/venv /app/venv

# Copy the rest of the application
COPY ./app /app

# Expose port 8040 to the outside world
EXPOSE 8050

# Define environment variables
ENV WORKERS=2
ENV UVICORN_CONCURRENCY=32
ENV PATH="/app/venv/bin:$PATH"

# Set the command to run your FastAPI application with Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8050 --workers $WORKERS --limit-concurrency $UVICORN_CONCURRENCY"]
