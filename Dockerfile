# Use an official Python runtime as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
