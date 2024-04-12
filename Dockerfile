# Use an official Python runtime as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Update the package list
RUN apt-get update -y

# Install the dependencies for WeasyPrint
RUN apt-get install -y --no-install-recommends python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Clean up
RUN rm -rf /var/lib/apt/lists/*

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
