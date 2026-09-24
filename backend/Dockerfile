FROM python:3.12-slim

WORKDIR /app

# Install curl for health checks and startup script
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["./start.sh"]
