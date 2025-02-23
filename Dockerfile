# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_VERSION=20 \
    PORT=8000 \
    PATH="/home/frequser/.local/bin:${PATH}"

# Create non-root user first
RUN useradd -m -s /bin/bash frequser

# Set working directory and change ownership
WORKDIR /freqtrade/user_data/FREQassistant
RUN chown frequser:frequser /freqtrade/user_data/FREQassistant

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    build-essential \
    sqlite3 \
    libsqlite3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY --chown=frequser:frequser requirements.txt .

# Switch to non-root user for pip installations
USER frequser

# Install Python dependencies with version pinning and error handling
RUN pip install --user --no-cache-dir -r requirements.txt || exit 1 && \
    pip install --user --no-cache-dir \
    "uvicorn[standard]>=0.24.0,<0.25.0" \
    "gunicorn>=21.2.0,<22.0.0" \
    "fastapi>=0.104.0,<0.105.0" || exit 1

# Copy project files after installing dependencies
COPY --chown=frequser:frequser . .

# Ensure proper permissions
USER root
RUN chmod +x main.py && \
    chown -R frequser:frequser /freqtrade/user_data/FREQassistant

# Switch back to non-root user
USER frequser

# MODIFIED: Skip frontend build and create empty build directory
WORKDIR /freqtrade/user_data/FREQassistant/frontend
RUN mkdir -p /freqtrade/user_data/FREQassistant/frontend/build || true

# Return to main directory
WORKDIR /freqtrade/user_data/FREQassistant

# Create necessary directories with proper permissions
USER root
RUN mkdir -p /freqtrade/user_data/FREQassistant/logs /freqtrade/user_data/FREQassistant/data && \
    chmod 755 /freqtrade/user_data/FREQassistant/logs /freqtrade/user_data/FREQassistant/data && \
    chown -R frequser:frequser /freqtrade/user_data/FREQassistant

# Create and configure logging
RUN touch /freqtrade/user_data/FREQassistant/logging.conf && \
    chown frequser:frequser /freqtrade/user_data/FREQassistant/logging.conf && \
    chmod 644 /freqtrade/user_data/FREQassistant/logging.conf

# Switch back to non-root user
USER frequser

# Expose port
EXPOSE ${PORT}

# Health check with appropriate timing
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the application with proper logging
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.conf", "--workers", "4"]
