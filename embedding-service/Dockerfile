FROM python:3.10-slim

WORKDIR /app

# Install system packages for pdfplumber
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy common package first
COPY common/ /app/common/

# Copy service-specific files
COPY embedding-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY embedding-service/ .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
