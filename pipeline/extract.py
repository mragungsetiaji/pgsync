import os
import json
import asyncio
import psycopg
import uuid
import logging

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from celery import Celery
from celery.result import AsyncResult

from config import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
)
from services.redis import RedisClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("extract")

celery_app = Celery(
    "extract_tasks", 
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}", 
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)
if REDIS_PASSWORD:
    celery_app.conf.broker_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    celery_app.conf.result_backend = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_expires = 60*60*24  # 1 day

@dataclass
class ExtractJob:
    """Data class representing an extraction job."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    table_name: str = ""
    cursor_column: str = ""  # Column to use for incremental extraction
    cursor_value: Any = None  # Current value of the cursor
    batch_size: int = 1000
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_records: int = 0
    extracted_records: int = 0
    celery_task_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return asdict(self)

class DataExtractor:
    """Handles data extraction from PostgreSQL database."""
    
    def __init__(self, conn_params: Dict[str, Any]):
        """Initialize extractor with connection parameters."""
        self.conn_params = conn_params
        self.output_dir = os.path.join(os.getcwd(), "data", "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def extract_incremental(self, job_dict: Dict[str, Any]) -> bool:
        """
        Extract data incrementally from a table using cursor-based pagination.
        
        Args:
            job: The extraction job configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        job = ExtractJob(**job_dict)
        try:
            job.status = "running"
            job.updated_at = datetime.now().isoformat()
            
            # Get the total count for progress tracking (optional)
            total_count = await self._get_total_count(job.table_name, job.cursor_column, job.cursor_value)
            job.total_records = total_count
            
            # Initialize cursor value if not set
            cursor_value = job.cursor_value
            
            # Keep extracting until no more records
            has_more_data = True
            batch_num = 0

            while has_more_data:
                # Extract a batch of data
                batch_data, next_cursor_value = await self._extract_batch(
                    job.table_name, 
                    job.cursor_column, 
                    cursor_value, 
                    job.batch_size
                )
                
                # If we got fewer records than batch_size or same cursor, we're done
                if len(batch_data) < job.batch_size or next_cursor_value == cursor_value:
                    has_more_data = False
                
                # Save the data batch if we got any records
                if batch_data:
                    batch_num += 1
                    file_path = self._get_output_path(job.table_name, job.id, batch_num)
                    self._save_to_json(batch_data, file_path)
                    
                    # Update job status
                    job.extracted_records += len(batch_data)
                    job.updated_at = datetime.now().isoformat()
                    job.cursor_value = next_cursor_value
                    cursor_value = next_cursor_value

                    # Store updated job status
                    update_job_status(job)
                else:
                    has_more_data = False
            
            # Mark job as completed
            job.status = "completed"
            job.updated_at = datetime.now().isoformat()
            update_job_status(job)
            return True
        
        except Exception as e:
            # Handle errors
            logger.error(f"Error extracting data: {str(e)}")
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.now().isoformat()
            update_job_status(job)
            return False
        
    async def _get_total_count(self, table_name: str, cursor_column: str, cursor_value: Any) -> int:
        """Get total record count for a table."""
        where_clause = ""
        params = []
        
        if cursor_value is not None:
            where_clause = f"WHERE {cursor_column} > %s"
            params = [cursor_value]
            
        query = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
        
        async with await psycopg.AsyncConnection.connect(**self.conn_params) as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                result = await cur.fetchone()
                return result[0] if result else 0
        
    async def _extract_batch(self, table_name: str, cursor_column: str, cursor_value: Any, batch_size: int):
        """Extract a batch of data from a table."""
        where_clause = ""
        params = [batch_size]
        
        if cursor_value is not None:
            where_clause = f"WHERE {cursor_column} > %s"
            params = [cursor_value, batch_size]
            
        query = f"""
        SELECT * FROM {table_name} 
        {where_clause}
        ORDER BY {cursor_column} ASC 
        LIMIT %s
        """
        
        async with await psycopg.AsyncConnection.connect(**self.conn_params) as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                batch_data = []
                
                # Fetch all rows in the batch
                rows = await cur.fetchall()
                
                for row in rows:
                    # Convert row to dict with column names
                    row_dict = {columns[i]: value for i, value in enumerate(row)}
                    batch_data.append(row_dict)
                
                # Get the new cursor value (last row's cursor column)
                next_cursor_value = rows[-1][columns.index(cursor_column)] if rows else cursor_value
                
                return batch_data, next_cursor_value
            
    def _get_output_path(self, table_name: str, job_id: str, batch_num: int) -> str:
        """Generate output file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{table_name}_{job_id}_{batch_num}_{timestamp}.json"
        return os.path.join(self.output_dir, filename)
    
    def _save_to_json(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Save data to a JSON file."""
        with open(file_path, "w") as f:
            json.dump(data, f)
        logger.info(f"Saved {len(data)} records to {file_path}")

# Celery tasks
@celery_app.task(name="extract.process_job", bind=True)
def process_job_task(self, job_dict, conn_params) -> None:
    """Celery task to process a job."""
    task_id = self.request.id
    job_dict['celery_task_id'] = task_id
    job_dict['status'] = 'running'
    job_dict['updated_at'] = datetime.now().isoformat()
    
    # Store updated job in Redis
    update_job_status(ExtractJob(**job_dict))
    
    # Use connection parameters passed from the route
    extractor = DataExtractor(conn_params)
    result = asyncio.run(extractor.extract_incremental(job_dict))
    return result

def add_extract_job(
    source_db_id: int,
    table_name: str, 
    cursor_column: str, 
    cursor_value: Any = None, 
    batch_size: int = 1000,
    conn_params: Dict[str, Any] = None
) -> ExtractJob:
    """
    Add a new extraction job to the queue using Celery.
    
    Args:
        source_db_id: ID of the source database
        table_name: Name of the table to extract
        cursor_column: Column to use for incremental extraction
        cursor_value: Starting value for the cursor (None for beginning)
        batch_size: Number of records to fetch in each batch
        conn_params: Database connection parameters
        
    Returns:
        ExtractJob: The created job
    """
    job = ExtractJob(
        source_db_id=source_db_id,
        table_name=table_name,
        cursor_column=cursor_column,
        cursor_value=cursor_value,
        batch_size=batch_size
    )
    
    # Submit job to Celery
    job_dict = job.to_dict()
    result = process_job_task.delay(job_dict, conn_params)
    job.celery_task_id = result.id
    
    # Store initial job status
    update_job_status(job)
    
    logger.info(f"Added job {job.id} to Celery queue for table {table_name}")
    return job

def update_job_status(job: ExtractJob) -> None:
    """Update job status in Redis."""
    redis_client = RedisClient(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD
    )
    
    redis_client.set(f"job:{job.id}", json.dumps(job.to_dict()))

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a job from Redis."""
    redis_client = RedisClient(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD
    )
    
    job_data = redis_client.get(f"job:{job_id}")
    if job_data:
        return json.loads(job_data)
    
    # Check Celery status if job not in Redis
    task = AsyncResult(job_id, app=celery_app)
    if task.state:
        return {
            "id": job_id,
            "status": task.state.lower(),
            "error": str(task.result) if task.failed() else None
        }
    
    return None

def list_jobs() -> Dict[str, Any]:
    """List all jobs from Redis."""
    redis_client = RedisClient(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD
    )
    
    # Get all job keys
    job_keys = redis_client.client.keys("job:*")
    
    active_jobs = []
    completed_jobs = []
    
    for key in job_keys:
        job_data = json.loads(redis_client.get(key))
        if job_data["status"] in ["pending", "running"]:
            active_jobs.append(job_data)
        else:
            completed_jobs.append(job_data)
    
    return {
        "active": active_jobs,
        "completed": completed_jobs
    }