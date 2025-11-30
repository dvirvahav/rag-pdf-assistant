import pika
import json
from typing import Any, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path to import common package
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from common.event_types import EventType

from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_QUEUE


def publish_audit_event(event_type: EventType, payload: Optional[Dict[str, Any]] = None) -> bool:
    """
    Publish an audit event to RabbitMQ for failure logging.

    Args:
        event_type: Type of the audit event (e.g., EXTRACTION_FAILED, EMBEDDING_FAILED)
        payload: Optional dictionary with additional event data (error details, filename, etc.)

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
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        # Prepare message
        message = {
            "event_type": event_type.value,
            "service_name": "embedding-service",
            "payload": payload
        }

        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )

        # Close connection
        connection.close()

        print(f"Audit event published: {event_type}")
        return True

    except Exception as e:
        # Log the error but don't raise - audit logging should not break the main flow
        print(f"Failed to publish audit event: {e}")
        return False
