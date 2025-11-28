import pika
import json
from typing import Any, Dict, Optional
from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, EMBEDDING_QUEUE


def publish_file_uploaded_event(job_id: str, filename: str, filepath: str) -> bool:
    """
    Publish a file uploaded event to RabbitMQ for the embedding service to process.
    
    Args:
        job_id: Unique job identifier for tracking status
        filename: Name of the uploaded file
        filepath: Full path to the uploaded file
        
    Returns:
        True if the message was published successfully, False otherwise.
    """
    try:
        # Create connection parameters
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        
        # Establish connection
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # Declare queue (creates if doesn't exist)
        channel.queue_declare(queue=EMBEDDING_QUEUE, durable=True)
        
        # Prepare message with job_id for status tracking
        message = {
            "event_type": "FILE_UPLOADED",
            "job_id": job_id,
            "filename": filename,
            "filepath": filepath
        }
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key=EMBEDDING_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        
        # Close connection
        connection.close()
        
        print(f"File uploaded event published for job {job_id}: {filename}")
        return True
        
    except Exception as e:
        # Log the error but don't raise - publishing should not break the upload flow
        print(f"Failed to publish file uploaded event: {e}")
        return False
