FROM python:3.8-slim

WORKDIR /app

# Install system dependencies including AWS CLI requirements
RUN apt-get update && apt-get install -y \
    git \
    libopenjp2-7-dev \
    build-essential \
    zlib1g-dev \
    libjpeg-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Keep container running
CMD ["tail", "-f", "/dev/null"]