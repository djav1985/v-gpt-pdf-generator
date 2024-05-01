# Use an official Python runtime based on Alpine as a parent image
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install system dependencies required for Python packages and optimize install process
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev && \
    pip install --no-cache-dir -r /app/requirements.txt

# Expose port 80 to the outside world
EXPOSE 8050

# Set an environment variable for workers with a default value
ENV UVICORN_WORKERS=3

# Command to run the app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050", "--workers", "${UVICORN_WORKERS}"]
