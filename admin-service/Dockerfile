FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY admin-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common package
COPY common/ ./common/

# Copy application code
COPY admin-service/app/ ./app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
