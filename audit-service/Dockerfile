FROM python:3.10-slim

WORKDIR /app

# Copy common package first
COPY common/ /app/common/

# Copy service-specific files
COPY audit-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY audit-service/ .

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
