#!/bin/sh

# Exit immediately if any command exits with a non-zero status
set -e

# Set the PYTHONPATH
export PYTHONPATH=/backend
echo "Current PYTHONPATH: $PYTHONPATH"
# cd /backend
# ls -R 
#  Wait for other db services to start (uncomment if needed)
echo "Waiting for database to be ready..."
# while ! nc -z host.docker.internal 5432; do  # Change 'database_host' to actual database host (localhost)
while ! nc -z postgres 5432; do
  sleep 1
done

# Optional: Check if main.py exists and log the result
if [ ! -f /backend/app/main.py ]; then
  echo "Error: /backend/app/main.py not found. Exiting."
  exit 1
fi

# Log the content of the /app directory for debugging
echo "Starting FastAPI Backend..."

# ls -la /code 

# Start the Uvicorn server
# exec uvicorn app.main:app --host 0.0.0.0 --port 8000

exec fastapi run app/main.py --host 0.0.0.0 --port 8000
