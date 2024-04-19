
# Use an official Python runtime based on Alpine as a parent image
FROM python:3.10-alpine


WORKDIR /app

# Install only the necessary build dependencies and clean up in one layer
RUN apk add --no-cache libffi-dev gcc musl-dev && \
    python -m venv /venv && \
    . /venv/bin/activate


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

