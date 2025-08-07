FROM python:3.12-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install configurable-http-proxy
RUN npm install -g configurable-http-proxy

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /data/CAST_ext/users
RUN chmod -R 755 /data/CAST_ext/users

# Expose port
EXPOSE 8080

# Command to run Gunicorn
CMD ["jupyterhub", "-f", "jupyterhub_config.py"]