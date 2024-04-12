#!/bin/bash

# Start cron in the background
cron -f &

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 80
