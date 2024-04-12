# Use an official Python runtime as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory in the container
WORKDIR /app
ENV PYTHONPATH=/app
# Install cron
RUN apt-get update && apt-get install -y cron

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./etc/cron.d/cleanup-cron /etc/cron.d/cleanup-cron


# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cleanup-cron

# Apply the cron job
RUN crontab /etc/cron.d/cleanup-cron

# Make the start.sh script executable
RUN chmod +x /app/start.sh

# Run the start script to handle both cron and FastAPI
CMD ["/app/start.sh"]
