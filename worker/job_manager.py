import os
import json
import logging
from celery.result import AsyncResult

from worker.celery_app import celery_app
from worker.redis_client import RedisClient
from core.jobs import ExtractJob, LoadJob

logger = logging.getLogger("job_manager")

def update_job_status(job):
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )

    # Determine job type and key
    if isinstance(job, ExtractJob):
        key = f"extract_job:{job.id}"
    elif isinstance(job, LoadJob):
        key = f"load_job:{job.id}"
    else:
        key = f"job:{job.id}"

    redis_client.set(key, json.dumps(job.to_dict()))

def get_job_status(job_id, job_type="extract"):
    """Get job status from Redis or Celery"""
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )
    
    # Try to get job from Redis
    key = f"{job_type}_job:{job_id}" if job_type else f"job:{job_id}"
    job_data = redis_client.get(key)
    if job_data:
        return json.loads(job_data)
    
    # Fall back to Celery for status
    if not job_type or job_type == "extract":
        # Try both keys for backward compatibility
        job_data = redis_client.get(f"job:{job_id}")
        if job_data:
            return json.loads(job_data)
    
    # Check Celery task status as last resort
    task = AsyncResult(job_id, app=celery_app)
    if task.state:
        return {
            "id": job_id,
            "status": task.state.lower(),
            "error": str(task.result) if task.failed() else None
        }
    
    return None

def list_jobs(job_type=None):
    """List jobs from Redis, optionally filtered by job_type"""
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )
    
    # Determine pattern based on job_type
    if job_type == "extract":
        patterns = ["extract_job:*", "job:*"]  # For backward compatibility
    elif job_type == "load":
        patterns = ["load_job:*"]
    else:
        patterns = ["extract_job:*", "load_job:*", "job:*"]
    
    active_jobs = []
    completed_jobs = []
    
    # Get jobs matching the patterns
    for pattern in patterns:
        job_keys = redis_client.client.keys(pattern)
        for key in job_keys:
            job_data = json.loads(redis_client.get(key))
            if job_data.get("status") in ["pending", "running"]:
                active_jobs.append(job_data)
            else:
                completed_jobs.append(job_data)
    
    return {"active": active_jobs, "completed": completed_jobs}

def get_related_jobs(job_id, relationship_type):
    """Get related jobs based on relationship type"""
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )
    
    if relationship_type == "loads_for_extract":
        # Find all load jobs related to an extract job
        load_jobs = []
        load_job_keys = redis_client.client.keys("load_job:*")
        for key in load_job_keys:
            job_data = json.loads(redis_client.get(key))
            if job_data.get("extract_job_id") == job_id:
                load_jobs.append(job_data)
        return load_jobs
    
    return []