import redis
import json
from typing import Optional, Dict, Any
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB, JOB_STATUS_TTL


# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)


def set_job_status(job_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """
    Set the status of a job in Redis.
    
    Args:
        job_id: Unique job identifier
        status: Job status (processing, completed, failed)
        details: Optional additional details (error message, chunks_count, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        job_data = {
            "status": status,
            "details": details or {}
        }
        redis_client.setex(
            name=f"job:{job_id}",
            time=JOB_STATUS_TTL,
            value=json.dumps(job_data)
        )
        return True
    except Exception as e:
        print(f"Failed to set job status in Redis: {e}")
        return False


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the status of a job from Redis.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job data dict with status and details, or None if not found
    """
    try:
        data = redis_client.get(f"job:{job_id}")
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Failed to get job status from Redis: {e}")
        return None
