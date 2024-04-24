# Stage 1: Build environment
FROM python:3.11-alpine AS build
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install build dependencies
RUN apk update && \
    apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers

# Install Python packages
RUN pip install --no-cache-dir -r /app/requirements.txt

# Check if gunicorn is installed
RUN which gunicorn

# Remove build dependencies
RUN apk del .build-deps

# Stage 2: Runtime environment
FROM python:3.11-alpine
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app .

# Expose port
EXPOSE 8000

# Run the application with Gunicorn using Uvicorn workers
CMD ["gunicorn", "main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000"]
