# Use an official Python runtime as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install wkhtmltopdf
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        wget \
        xz-utils \
        fontconfig \
        libxrender1 \
        xfonts-75dpi \
        xfonts-base \
    && wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && dpkg -i wkhtmltox_0.12.5-1.buster_amd64.deb \
    && apt-get remove -y \
        wget \
        xz-utils \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm wkhtmltox_0.12.5-1.buster_amd64.deb

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
