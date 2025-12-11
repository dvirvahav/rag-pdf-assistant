#!/usr/bin/env python3
"""
RabbitMQ consumer for processing PDF upload jobs
Replaces the Celery worker functionality
"""
import json
import sys
import signal
import logging
from io import BytesIO

import pika

from backend.config import settings
from backend.services.job_status import job_status_service, JobStatus
from backend.services.storage import save_pdf
from backend.services.document_processing import extract_text_from_pdf, clean_text, chunk_text
from backend.services.embeddings import embed_chunks
from backend.services.vector_store import init_collection, is_file_indexed, upsert_chunks

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFProcessingConsumer:
    """Consumer for processing PDF upload jobs from RabbitMQ"""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "pdf_processing_queue"
        self.exchange_name = "pdf_processing_exchange"
        self.should_stop = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.should_stop = True
        if self.channel:
            self.channel.stop_consuming()

    def connect(self):
        """Connect to RabbitMQ"""
        try:
            connection_params = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(
                    settings.RABBITMQ_USER,
                    settings.RABBITMQ_PASSWORD
                ),
                heartbeat=600,  # 10 minutes
                blocked_connection_timeout=300  # 5 minutes
            )

            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()

            # Declare exchange and queue
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True
            )
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.queue_name
            )

            # Set QoS - only process one message at a time
            self.channel.basic_qos(prefetch_count=1)

            logger.info("Connected to RabbitMQ successfully")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def process_pdf_upload(self, job_id: str, file_data: dict):
        """
        Process PDF upload with job status tracking
        Same logic as the old Celery task
        """
        try:
            # Update job status to processing
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 10, "Initializing PDF processing"
            )

            # Extract file information from task data
            filename = file_data["filename"]
            filepath = file_data["filepath"]

            # Check that collection exists if not - create one
            init_collection()

            # Update progress
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 20, "Initializing collection"
            )

            # 2) Skip if already processed
            if is_file_indexed(filename):
                result = {
                    "status": "already_indexed",
                    "filename": filename
                }
                job_status_service.update_job_status(
                    job_id, JobStatus.COMPLETED, 100, "File already indexed", result=result
                )
                return result

            # Update progress
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 40, "Checking if file already indexed"
            )

            # 3) Extract text
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 50, "Extracting text from PDF"
            )
            raw_text = extract_text_from_pdf(filepath)

            # 4) Clean text
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 60, "Cleaning extracted text"
            )
            cleaned_text = clean_text(raw_text)

            # 5) Chunk text
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 70, "Chunking text"
            )
            chunks = chunk_text(cleaned_text)

            # 6) Embed chunks
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 80, "Generating embeddings"
            )
            vectors = embed_chunks(chunks)

            # 7) Save in Qdrant
            job_status_service.update_job_status(
                job_id, JobStatus.PROCESSING, 90, "Storing vectors in database"
            )
            upsert_chunks(vectors, chunks, filename)

            # Complete the job
            result = {
                "status": "indexed",
                "filename": filename,
                "chunks_count": len(chunks)
            }

            job_status_service.update_job_status(
                job_id, JobStatus.COMPLETED, 100, "PDF processing completed successfully", result=result
            )

            logger.info(f"Successfully processed PDF: {filename} (job_id: {job_id})")
            return result

        except Exception as e:
            # Update job status on failure
            error_msg = f"PDF processing failed: {str(e)}"
            job_status_service.update_job_status(
                job_id, JobStatus.FAILED, 0, error_msg, error=error_msg
            )
            logger.error(f"Failed to process PDF (job_id: {job_id}): {e}")
            raise  # Re-raise to mark message as failed

    def callback(self, ch, method, properties, body):
        """Callback function for processing messages"""
        try:
            # Parse message
            message = json.loads(body)
            job_id = message["job_id"]
            job_data = message["data"]

            logger.info(f"Received job: {job_id}")

            # Process the job
            self.process_pdf_upload(job_id, job_data)

            # Acknowledge successful processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Job {job_id} processed successfully")

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            # Reject the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages"""
        try:
            self.connect()

            # Set up consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )

            logger.info("Starting to consume messages. Press Ctrl+C to exit.")
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up connections"""
        if self.channel:
            try:
                self.channel.close()
            except:
                pass
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        logger.info("Consumer shutdown complete")


def main():
    """Main entry point"""
    consumer = PDFProcessingConsumer()
    try:
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"Consumer failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
