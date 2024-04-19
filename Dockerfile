# Use an official Python runtime as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10 AS builder

# Set the working directory in the container
WORKDIR /app

# Install dependencies in a virtual environment to keep the container clean
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends python3-dev libcairo2 libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Multi-stage build: Create a new stage with a cleaner base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy only the necessary binaries/libraries
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcairo.so.2 /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libpango-1.0.so.0 /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libpangoft2-1.0.so.0 /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libgdk_pixbuf-2.0.so.0 /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libffi.so.7 /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/share/mime /usr/share/

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
