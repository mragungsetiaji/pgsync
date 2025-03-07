import os
import json
import logging
from celery.result import AsyncResult

from worker.celery_app import celery_app
from worker.redis_client import RedisClient

logger = logging.getLogger("job_manager")

def update_job_status(job):
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )
    redis_client.set(f"job:{job.id}", json.dumps(job.to_dict()))

def get_job_status(job_id):
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )
    job_data = redis_client.get(f"job:{job_id}")
    if job_data:
        return json.loads(job_data)
    task = AsyncResult(job_id, app=celery_app)
    if task.state:
        return {"id": job_id, "status": task.state.lower(), "error": str(task.result) if task.failed() else None}
    return None

def list_jobs():
    redis_client = RedisClient(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD')
    )
    job_keys = redis_client.client.keys("job:*")
    active_jobs = []
    completed_jobs = []
    for key in job_keys:
        job_data = json.loads(redis_client.get(key))
        if job_data["status"] in ["pending", "running"]:
            active_jobs.append(job_data)
        else:
            completed_jobs.append(job_data)
    return {"active": active_jobs, "completed": completed_jobs}