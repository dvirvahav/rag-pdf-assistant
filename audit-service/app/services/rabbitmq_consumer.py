import pika
import json
import threading
import time
from typing import Callable
from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_QUEUE
from app.models.audit_event import AuditEventCreate
from app.services.postgres_service import create_audit_event


class RabbitMQConsumer:
    """
    RabbitMQ consumer that listens for audit events and stores them in PostgreSQL.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.is_running = False
        self._consumer_thread = None
    
    def _get_connection_params(self) -> pika.ConnectionParameters:
        """
        Get RabbitMQ connection parameters.
        """
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        return pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    
    def _connect(self) -> bool:
        """
        Establish connection to RabbitMQ with retry logic.
        """
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                print(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{max_retries})...")
                self.connection = pika.BlockingConnection(self._get_connection_params())
                self.channel = self.connection.channel()
                
                # Declare the queue (creates if doesn't exist)
                self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
                
                print(f"Successfully connected to RabbitMQ. Listening on queue: {RABBITMQ_QUEUE}")
                return True
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Failed to connect to RabbitMQ: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Could not connect to RabbitMQ.")
                    return False
        return False
    
    def _process_message(self, ch, method, properties, body):
        """
        Process incoming message from RabbitMQ queue.
        
        Args:
            ch: Channel
            method: Method frame
            properties: Message properties
            body: Message body (bytes)
        """
        try:
            # Parse the message body as JSON
            message_data = json.loads(body.decode('utf-8'))
            print(f"Received audit event: {message_data}")
            
            # Create audit event from message
            event_data = AuditEventCreate(
                event_type=message_data.get('event_type', 'UNKNOWN'),
                service_name=message_data.get('service_name', 'UNKNOWN'),
                payload=message_data.get('payload')
            )
            
            # Store in PostgreSQL
            created_event = create_audit_event(event_data)
            print(f"Stored audit event with ID: {created_event.id}")
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse message as JSON: {e}")
            # Reject the message without requeue (dead letter)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print(f"Error processing message: {e}")
            # Requeue the message for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def _consume(self):
        """
        Start consuming messages from the queue.
        """
        if not self._connect():
            return
        
        # Set prefetch count to process one message at a time
        self.channel.basic_qos(prefetch_count=1)
        
        # Start consuming
        self.channel.basic_consume(
            queue=RABBITMQ_QUEUE,
            on_message_callback=self._process_message
        )
        
        self.is_running = True
        print("Starting to consume messages...")
        
        try:
            while self.is_running:
                self.connection.process_data_events(time_limit=1)
        except Exception as e:
            print(f"Consumer error: {e}")
        finally:
            self._close()
    
    def start(self):
        """
        Start the consumer in a background thread.
        """
        if self._consumer_thread is not None and self._consumer_thread.is_alive():
            print("Consumer is already running")
            return
        
        self._consumer_thread = threading.Thread(target=self._consume, daemon=True)
        self._consumer_thread.start()
        print("RabbitMQ consumer started in background thread")
    
    def stop(self):
        """
        Stop the consumer.
        """
        self.is_running = False
        if self._consumer_thread is not None:
            self._consumer_thread.join(timeout=5)
        print("RabbitMQ consumer stopped")
    
    def _close(self):
        """
        Close the RabbitMQ connection.
        """
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            print("RabbitMQ connection closed")
        except Exception as e:
            print(f"Error closing RabbitMQ connection: {e}")


# Global consumer instance
consumer = RabbitMQConsumer()
