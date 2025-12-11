"""
RabbitMQ producer service for job queuing
"""
import json
import pika
from backend.config import settings


class RabbitMQProducer:
    """Service for publishing jobs to RabbitMQ"""

    def __init__(self):
        self.connection_params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
        )
        self.queue_name = "pdf_processing_queue"
        self.exchange_name = "pdf_processing_exchange"

    def publish_job(self, job_id: str, job_data: dict):
        """Publish a job to the RabbitMQ queue"""
        connection = None
        channel = None
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()

            # Declare exchange and queue
            channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True
            )
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.queue_name
            )

            # Prepare message
            message = {
                "job_id": job_id,
                "data": job_data
            }

            # Publish message
            channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

        except Exception as e:
            raise Exception(f"Failed to publish job to RabbitMQ: {str(e)}")
        finally:
            if channel:
                channel.close()
            if connection:
                connection.close()


# Global producer instance
rabbitmq_producer = RabbitMQProducer()
