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

# Install the dependencies
RUN apt-get install -y --no-install-recommends wget xz-utils fontconfig libxrender1 xfonts-75dpi xfonts-base

# Download wkhtmltopdf
RUN wget wget http://download.gna.org/wkhtmltopdf/0.12/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb

# Install wkhtmltopdf
RUN dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb

# Remove unnecessary packages
RUN apt-get remove -y wget xz-utils

# Auto remove unnecessary dependencies
RUN apt-get autoremove -y

# Clean up
RUN rm -rf /var/lib/apt/lists/*
RUN rm wkhtmltox-0.12.1_linux-trusty-amd64.deb

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
