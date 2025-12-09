"""
Job status tracking service using Redis
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

import redis

from backend.config import settings


class JobStatus(Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatusService:
    """Service for tracking job status using Redis"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.job_prefix = "job:"

    def create_job(self, job_type: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        job_key = f"{self.job_prefix}{job_id}"

        job_data = {
            "id": job_id,
            "type": job_type,
            "status": JobStatus.QUEUED.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "message": "Job queued",
            "metadata": metadata or {},
            "result": None,
            "error": None
        }

        self.redis_client.set(job_key, json.dumps(job_data))
        # Set expiration to 24 hours
        self.redis_client.expire(job_key, 86400)

        return job_id

    def update_job_status(self, job_id: str, status: JobStatus,
                         progress: int = 0, message: str = "",
                         result: Any = None, error: str = None):
        """Update job status"""
        job_key = f"{self.job_prefix}{job_id}"
        job_data = self.get_job(job_id)

        if not job_data:
            return

        job_data["status"] = status.value
        job_data["progress"] = progress
        job_data["message"] = message
        job_data["updated_at"] = datetime.utcnow().isoformat()

        if result is not None:
            job_data["result"] = result
        if error is not None:
            job_data["error"] = error

        self.redis_client.set(job_key, json.dumps(job_data))

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data by ID"""
        job_key = f"{self.job_prefix}{job_id}"
        job_data = self.redis_client.get(job_key)

        if not job_data:
            return None

        return json.loads(job_data)

    def delete_job(self, job_id: str):
        """Delete job from Redis"""
        job_key = f"{self.job_prefix}{job_id}"
        self.redis_client.delete(job_key)

    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get all jobs (for debugging/admin purposes)"""
        jobs = {}
        for key in self.redis_client.scan_iter(f"{self.job_prefix}*"):
            job_id = key.replace(self.job_prefix, "")
            job_data = self.get_job(job_id)
            if job_data:
                jobs[job_id] = job_data
        return jobs


# Global job status service instance
job_status_service = JobStatusService()
