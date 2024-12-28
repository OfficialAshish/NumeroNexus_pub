FROM python:3.10-slim

WORKDIR /backend

COPY requirements.txt .

RUN apt-get update -y && \
    apt-get clean && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure entrypoint.sh is executable
RUN chmod +x /backend/entrypoint.sh

EXPOSE 8000

# Using entrypoint.sh to start the application
ENTRYPOINT ["sh", "/backend/entrypoint.sh"]
