import pika
import json
import threading
import time
from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, EMBEDDING_QUEUE
from app.pipeline.pdf_pipeline import process_file
from app.services.redis_service import set_job_status


class EmbeddingConsumer:
    """
    RabbitMQ consumer that listens for file upload events and triggers the embedding pipeline.
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
                self.channel.queue_declare(queue=EMBEDDING_QUEUE, durable=True)
                
                print(f"Successfully connected to RabbitMQ. Listening on queue: {EMBEDDING_QUEUE}")
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
        Updates job status in Redis upon completion or failure.
        
        Args:
            ch: Channel
            method: Method frame
            properties: Message properties
            body: Message body (bytes)
        """
        job_id = None
        try:
            # Parse the message body as JSON
            message_data = json.loads(body.decode('utf-8'))
            print(f"Received file upload event: {message_data}")
            
            event_type = message_data.get('event_type')
            job_id = message_data.get('job_id')
            filename = message_data.get('filename')
            
            if event_type == 'FILE_UPLOADED' and filename and job_id:
                print(f"Starting embedding pipeline for job {job_id}: {filename}")
                
                # Process the file through the embedding pipeline
                result = process_file(filename)
                print(f"Embedding pipeline result: {result}")
                
                # Update job status in Redis based on result
                if result.get('status') == 'indexed':
                    set_job_status(job_id, "completed", {
                        "filename": filename,
                        "chunks_count": result.get('chunks_count', 0)
                    })
                    print(f"Job {job_id} completed successfully")
                else:
                    # Processing failed
                    set_job_status(job_id, "failed", {
                        "filename": filename,
                        "error": result.get('error', 'unknown_error'),
                        "details": result.get('details', '')
                    })
                    print(f"Job {job_id} failed: {result.get('error')}")
                
                # Acknowledge the message after processing
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f"Unknown event type or missing filename/job_id: {message_data}")
                # Acknowledge to remove from queue (invalid message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse message as JSON: {e}")
            # Reject the message without requeue (dead letter)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print(f"Error processing message: {e}")
            # Update job status to failed if we have job_id
            if job_id:
                set_job_status(job_id, "failed", {
                    "error": "processing_exception",
                    "details": str(e)
                })
            # Reject without requeue to avoid infinite loop
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
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
            queue=EMBEDDING_QUEUE,
            on_message_callback=self._process_message
        )
        
        self.is_running = True
        print("Starting to consume file upload events...")
        
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
        print("Embedding consumer started in background thread")
    
    def stop(self):
        """
        Stop the consumer.
        """
        self.is_running = False
        if self._consumer_thread is not None:
            self._consumer_thread.join(timeout=5)
        print("Embedding consumer stopped")
    
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
embedding_consumer = EmbeddingConsumer()
