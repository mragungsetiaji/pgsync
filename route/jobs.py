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
    
@router.post("/create")
async def create_job(etl_job: dict):
    """Create a combined extract-transform-load job"""
    try:
        from worker.tasks import add_etl_job
        
        # Validate required fields
        required_fields = {
            "source": ["table_name", "conn_params"],
            "destination": ["type", "config", "dataset", "table"]
        }
        
        for category, fields in required_fields.items():
            if category not in etl_job:
                raise HTTPException(status_code=400, detail=f"Missing '{category}' configuration")
            
            for field in fields:
                if field not in etl_job[category]:
                    raise HTTPException(status_code=400, detail=f"Missing '{field}' in {category} configuration")
        
        # Extract source fields
        source = etl_job["source"]
        destination = etl_job["destination"]
        
        # Create ETL job
        job = add_etl_job(
            source_db_id=source.get("id", "default"),
            table_name=source["table_name"],
            conn_params=source["conn_params"],
            destination_config=destination["config"],
            dataset=destination["dataset"],
            table=destination["table"],
            use_ctid=source.get("use_ctid", True),
            cursor_column=source.get("cursor_column"),
            cursor_value=source.get("cursor_value"),
            batch_size=source.get("batch_size", 1000)
        )
        
        return {
            "message": "ETL job created successfully",
            "job_id": job.id
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating ETL job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))