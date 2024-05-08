# Use a slimmer Python image as base
FROM python:3.9-slim as base

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libgirepository1.0-dev \
    gobject-introspection \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file
COPY ./app/requirements.txt /app/

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./app /app

# Expose port 8050 to the outside world (make sure this matches your application's port)
EXPOSE 8050

# Define environment variables
ENV WORKERS=1
ENV UVICORN_CONCURRENCY=32

# Set the command to run your FastAPI application with Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8050 --workers $WORKERS --limit-concurrency $UVICORN_CONCURRENCY"]
