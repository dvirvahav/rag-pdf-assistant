FROM python:3.10-slim

WORKDIR /app

# Copy common package first
COPY common/ /app/common/

# Copy service-specific files
COPY file-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY file-service/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
