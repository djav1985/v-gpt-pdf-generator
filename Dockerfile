# Stage 1: Build environment
FROM python:3.11-alpine AS build
WORKDIR /app

# Install build dependencies and Python packages in a single RUN command
RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copy application files
COPY . .

# Stage 2: Runtime environment
FROM python:3.11-alpine
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
