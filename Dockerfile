# Use an official Python runtime based on Alpine as a parent image
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install necessary system dependencies and Python packages in one RUN command
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev && \
    pip install --no-cache-dir -r /app/requirements.txt

# Expose port 80 to the outside world
EXPOSE 80

# Run the FastAPI application using Gunicorn with Uvicorn workers
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
