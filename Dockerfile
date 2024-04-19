# Use a lighter base image if possible, such as an Alpine version
FROM python:3.10-alpine AS builder

WORKDIR /app

# Install only the necessary build dependencies and clean up in one layer
RUN apk add --no-cache libffi-dev gcc musl-dev && \
    python -m venv /venv && \
    . /venv/bin/activate

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    find /venv -type d -name __pycache__ -exec rm -rf {} +

# Final stage: Use the same base image for consistency
FROM python:3.10-alpine

WORKDIR /app
COPY --from=builder /venv /venv

ENV PATH="/venv/bin:$PATH"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
