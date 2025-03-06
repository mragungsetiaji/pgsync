from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.database import Source, ExtractionJob
from session_manager import get_db_session
from models.api import ExtractJobCreate, ExtractJobResponse, StatusResponse

from pipeline.extract import add_extract_job, get_job_status
from services.postgres import Postgres

router = APIRouter(
    prefix="/extractions",
    tags=["Data Extraction"]
)

@router.post("/", response_model=ExtractJobResponse)
def create_extraction_job(job_data: ExtractJobCreate, db: Session = Depends(get_db_session)):
    """Create a new extraction job"""
    # Check if source database exists
    source_db = db.query(Source).filter(Source.id == job_data.source_db_id).first()
    if not source_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {job_data.source_db_id} not found"
        )
    
    # Validate that the table exists
    postgres = Postgres(
        host=source_db.host,
        port=source_db.port,
        database=source_db.database,
        user=source_db.user,
        password=source_db.password
    )
    
    # Check if table exists
    tables = postgres.fetch_tables()
    if job_data.table_name not in tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table '{job_data.table_name}' not found in source database"
        )
    
    # Check if cursor column exists
    columns = postgres.fetch_columns(job_data.table_name)
    column_names = [col["name"] for col in columns]
    if job_data.cursor_column not in column_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{job_data.cursor_column}' not found in table '{job_data.table_name}'"
        )
    
    # Create connection params for the data source
    conn_params = {
        "host": source_db.host,
        "port": source_db.port,
        "dbname": source_db.database,
        "user": source_db.user,
        "password": source_db.password
    }
    
    # Add job to queue
    job = add_extract_job(
        source_db_id=job_data.source_db_id,
        table_name=job_data.table_name,
        cursor_column=job_data.cursor_column,
        cursor_value=job_data.cursor_value,
        batch_size=job_data.batch_size,
        conn_params=conn_params
    )
    
    # Save job to database
    db_job = ExtractionJob(
        id=job.id,
        source_db_id=job_data.source_db_id,
        table_name=job_data.table_name,
        cursor_column=job_data.cursor_column,
        cursor_value=str(job_data.cursor_value) if job_data.cursor_value is not None else None,
        batch_size=job_data.batch_size,
        status="pending"
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job.to_dict()

@router.get("/", response_model=List[ExtractJobResponse])
def get_extraction_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """Get all extraction jobs"""
    jobs = db.query(ExtractionJob).offset(skip).limit(limit).all()
    return [job.to_dict() for job in jobs]

@router.get("/{job_id}", response_model=ExtractJobResponse)
def get_extraction_job(job_id: str, db: Session = Depends(get_db_session)):
    """Get a specific extraction job"""
    # First check the runtime jobs
    runtime_job = get_job_status(job_id)
    
    # Then check the database
    db_job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction job with ID {job_id} not found"
        )
    
    # If we have runtime info, update the database record
    if runtime_job:
        db_job.status = runtime_job["status"]
        db_job.error = runtime_job.get("error")
        db_job.total_records = runtime_job.get("total_records", 0)
        db_job.extracted_records = runtime_job.get("extracted_records", 0)
        db_job.cursor_value = str(runtime_job.get("cursor_value")) if runtime_job.get("cursor_value") is not None else None
        
        db.commit()
        db.refresh(db_job)
    
    return db_job.to_dict()

@router.get("/{job_id}/status", response_model=StatusResponse)
def get_extraction_job_status(job_id: str, db: Session = Depends(get_db_session)):
    """Get the status of a specific extraction job"""
    # Check runtime jobs
    runtime_job = get_job_status(job_id)
    
    # Check database
    db_job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction job with ID {job_id} not found"
        )
    
    status_message = runtime_job["status"] if runtime_job else db_job.status
    
    return {
        "status": "success",
        "message": f"Job status: {status_message}"
    }