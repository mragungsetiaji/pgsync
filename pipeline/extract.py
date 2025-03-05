import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg
from queue import Queue
import threading
import uuid
from dataclasses import dataclass, field, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("extract")

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return asdict(self)
    
# Global job queue
job_queue: Queue = Queue()
active_jobs: Dict[str, ExtractJob] = {}
completed_jobs: Dict[str, ExtractJob] = {}

class DataExtractor:
    """Handles data extraction from PostgreSQL database."""
    
    def __init__(self, conn_params: Dict[str, Any]):
        """Initialize extractor with connection parameters."""
        self.conn_params = conn_params
        self.output_dir = os.path.join(os.getcwd(), "extracted_data")
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def extract_incremental(self, job: ExtractJob) -> bool:
        """
        Extract data incrementally from a table using cursor-based pagination.
        
        Args:
            job: The extraction job configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
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
                else:
                    has_more_data = False
                
                # Simulating network delay for non-local testing
                await asyncio.sleep(0.1)
            
            # Mark job as completed
            job.status = "completed"
            job.updated_at = datetime.now().isoformat()
            return True
        
        except Exception as e:
            # Handle errors
            logger.error(f"Error extracting data: {str(e)}")
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.now().isoformat()
            return False
        
    async def _get_total_count(self, table_name: str, cursor_column: str, cursor_value: Any) -> int:
        """Get total count of records for progress tracking."""
        try:
            async with await psycopg.AsyncConnection.connect(**self.conn_params) as conn:
                async with conn.cursor() as cur:
                    query = f"SELECT COUNT(*) FROM {table_name}"
                    if cursor_value is not None:
                        query += f" WHERE {cursor_column} > %s"
                        await cur.execute(query, (cursor_value,))
                    else:
                        await cur.execute(query)
                    
                    result = await cur.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting count: {str(e)}")
            return 0
        
    async def _extract_batch(
        self, 
        table_name: str, 
        cursor_column: str, 
        cursor_value: Any, 
        batch_size: int
    ) -> tuple[List[Dict[str, Any]], Any]:
        """Extract a batch of data using cursor-based pagination."""
        async with await psycopg.AsyncConnection.connect(**self.conn_params) as conn:
            # Use row_factory to get dictionaries
            async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                # Build query based on whether we have a cursor value
                if cursor_value is not None:
                    query = f"""
                        SELECT * FROM {table_name} 
                        WHERE {cursor_column} > %s 
                        ORDER BY {cursor_column} ASC 
                        LIMIT %s
                    """
                    await cur.execute(query, (cursor_value, batch_size))
                else:
                    query = f"""
                        SELECT * FROM {table_name} 
                        ORDER BY {cursor_column} ASC 
                        LIMIT %s
                    """
                    await cur.execute(query, (batch_size,))
                
                # Fetch results
                results = await cur.fetchall()
                
                # Get the next cursor value if we have results
                next_cursor_value = cursor_value
                if results and len(results) > 0:
                    next_cursor_value = results[-1][cursor_column]
                
                return results, next_cursor_value
            
    def _get_output_path(self, table_name: str, job_id: str, batch_num: int) -> str:
        """Generate output file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{table_name}_{job_id}_{batch_num}_{timestamp}.json"
        return os.path.join(self.output_dir, filename)
    
    def _save_to_json(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Save data as JSON file."""
        # Custom JSON encoder to handle non-serializable types
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, (bytes, bytearray)):
                    return obj.hex()
                return json.JSONEncoder.default(self, obj)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, cls=CustomJSONEncoder, indent=2)
        
        logger.info(f"Saved {len(data)} records to {file_path}")

# Worker functions
async def process_job(extractor: DataExtractor, job: ExtractJob) -> None:
    """Process a single extraction job."""
    logger.info(f"Processing job {job.id} for table {job.table_name}")
    
    try:
        # Add to active jobs
        active_jobs[job.id] = job
        
        # Execute the extraction
        await extractor.extract_incremental(job)
        
        # Move to completed jobs
        if job.id in active_jobs:
            del active_jobs[job.id]
        completed_jobs[job.id] = job
        
        logger.info(f"Job {job.id} completed with status: {job.status}")
    
    except Exception as e:
        logger.error(f"Error processing job {job.id}: {str(e)}")
        job.status = "failed"
        job.error = str(e)
        job.updated_at = datetime.now().isoformat()
        
        # Move to completed jobs (with failed status)
        if job.id in active_jobs:
            del active_jobs[job.id]
        completed_jobs[job.id] = job

async def worker_loop(conn_params: Dict[str, Any]) -> None:
    """Background worker loop to process extraction jobs."""
    extractor = DataExtractor(conn_params)
    logger.info("Worker started")
    
    while True:
        try:
            # Check if we have jobs in the queue
            if not job_queue.empty():
                job = job_queue.get()
                await process_job(extractor, job)
                job_queue.task_done()
            else:
                # Wait a bit before checking again
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            await asyncio.sleep(5)  # Wait a bit longer after errors

def start_worker(conn_params: Dict[str, Any]) -> None:
    """Start the background worker in a separate thread."""
    async def run_worker():
        await worker_loop(conn_params)
    
    def thread_target():
        asyncio.run(run_worker())
    
    worker_thread = threading.Thread(target=thread_target, daemon=True)
    worker_thread.start()
    logger.info("Worker thread started")

def add_extract_job(
    table_name: str, 
    cursor_column: str, 
    cursor_value: Any = None, 
    batch_size: int = 1000
) -> ExtractJob:
    """
    Add a new extraction job to the queue.
    
    Args:
        table_name: Name of the table to extract
        cursor_column: Column to use for incremental extraction
        cursor_value: Starting value for the cursor (None for beginning)
        batch_size: Number of records to fetch in each batch
        
    Returns:
        ExtractJob: The created job
    """
    job = ExtractJob(
        table_name=table_name,
        cursor_column=cursor_column,
        cursor_value=cursor_value,
        batch_size=batch_size
    )
    
    job_queue.put(job)
    logger.info(f"Added job {job.id} to queue for table {table_name}")
    return job

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a job."""
    if job_id in active_jobs:
        return active_jobs[job_id].to_dict()
    elif job_id in completed_jobs:
        return completed_jobs[job_id].to_dict()
    return None

def list_jobs() -> Dict[str, Any]:
    """List all jobs."""
    return {
        "active": [job.to_dict() for job in active_jobs.values()],
        "completed": [job.to_dict() for job in completed_jobs.values()]
    }