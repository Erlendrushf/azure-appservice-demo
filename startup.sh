#!/bin/bash
# Startup script for Azure App Service

# Use the PORT environment variable if set, otherwise default to 8000
PORT=${PORT:-8000}

# Start gunicorn with uvicorn workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile -
