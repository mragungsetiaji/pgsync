from fastapi import APIRouter, HTTPException
from typing import Optional

from utils import logger
from worker.job_manager import get_job_status

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)
    
@router.post("/transform/{extract_job_id}")
async def transform_data(extract_job_id: str, generation_id: Optional[str] = None):
    """Transform extracted data to Airbyte format"""
    try:
        from worker.tasks import process_transform_task
        
        # Check that the extract job exists and is completed
        extract_job = get_job_status(extract_job_id)
        if not extract_job:
            raise HTTPException(status_code=404, detail=f"Extract job {extract_job_id} not found")
        
        if extract_job.get("status") != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Extract job {extract_job_id} is not completed (status: {extract_job.get('status')})"
            )
        
        # Queue transform task
        result = process_transform_task.delay(extract_job_id, generation_id)
        
        return {
            "message": "Data transformation job queued successfully",
            "task_id": result.id,
            "extract_job_id": extract_job_id
        }
    except Exception as e:
        logger.error(f"Error queuing transformation job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load")
async def load_data(load_job: dict):
    """Load transformed data to destination"""
    try:
        from worker.tasks import add_load_job
        
        required_fields = ["extract_job_id", "destination_type", "destination_config", "dataset", "table"]
        for field in required_fields:
            if field not in load_job:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create and queue load job
        job = add_load_job(
            load_job["extract_job_id"],
            load_job["destination_type"],
            load_job["destination_config"],
            load_job["dataset"],
            load_job["table"]
        )
        
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create load job")
        
        return {
            "message": "Load job created successfully",
            "job_id": job.id,
            "status": job.status
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating load job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))