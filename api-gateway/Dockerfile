FROM python:3.10-slim

WORKDIR /app

# Copy common package
COPY common/ /app/common/

# Copy api-gateway files
COPY api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api-gateway/app/ /app/app/

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
