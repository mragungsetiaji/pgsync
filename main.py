from fastapi import FastAPI, HTTPException, Depends
from config import get_db
from source.postgres import Postgres
from models.api import StatusResponse, QueryRequest, ConnectionInfo
from typing import List, Dict, Any
import os

from pipeline.extract import start_worker, add_extract_job, list_jobs, get_job_status
from models.api import ExtractRequest, JobResponse

app = FastAPI(
    title="PostgreSQL Database Explorer",
    description="API to explore PostgreSQL database structure and execute queries",
    version="1.0.0"
)

# Start worker process when app starts
@app.lifespan("startup")
async def startup_event():
    # Get database connection info from environment variables
    conn_params = {
        "host": os.getenv("PG_HOST", "localhost"),
        "port": int(os.getenv("PG_PORT", "5432")),
        "dbname": os.getenv("PG_DATABASE", "postgres"),
        "user": os.getenv("PG_USER", "postgres"),
        "password": os.getenv("PG_PASSWORD", "postgres")
    }
    start_worker(conn_params)

@app.get("/", response_model=StatusResponse)
def root():
    """Health check endpoint"""
    return {"status": "success", "message": "PostgreSQL API is running"}

@app.get("/connection", response_model=StatusResponse)
def check_connection(db: Postgres = Depends(get_db)):
    """Check if database connection is working"""
    if db.check_connection():
        return {"status": "success", "message": "Database connection successful"}
    else:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

@app.get("/tables", response_model=List[str])
def get_tables(db: Postgres = Depends(get_db)):
    """Get all tables in database"""
    tables = db.fetch_tables()
    if tables:
        return tables
    else:
        return []

@app.get("/tables/{table_name}/columns", response_model=List[Dict[str, Any]])
def get_columns(table_name: str, db: Postgres = Depends(get_db)):
    """Get columns for a specific table"""
    columns = db.fetch_columns(table_name)
    if columns:
        return columns
    else:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found or has no columns")

@app.get("/schema", response_model=Dict[str, List[Dict[str, Any]]])
def get_schema(db: Postgres = Depends(get_db)):
    """Get complete database schema (all tables with their columns)"""
    schema = db.fetch_all_tables_with_columns()
    return schema

@app.post("/query", response_model=List[Dict[str, Any]])
def execute_query(query_req: QueryRequest, db: Postgres = Depends(get_db)):
    """Execute a custom SQL query"""
    try:
        params = tuple(query_req.params) if query_req.params else None
        result = db.execute_query(query_req.query, params)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")

@app.post("/connection/custom", response_model=StatusResponse)
def set_custom_connection(conn_info: ConnectionInfo):
    """Test connection with custom connection parameters"""
    db = Postgres(
        host=conn_info.host,
        port=conn_info.port,
        database=conn_info.database,
        user=conn_info.user,
        password=conn_info.password
    )

    if db.check_connection():
        return {"status": "success", "message": "Connection successful with provided parameters"}
    else:
        raise HTTPException(status_code=500, detail="Failed to connect with provided parameters")

@app.post("/extract", response_model=JobResponse)
def create_extract_job(request: ExtractRequest):
    """Create a new incremental extract job"""
    job = add_extract_job(
        table_name=request.table_name,
        cursor_column=request.cursor_column,
        cursor_value=request.cursor_value,
        batch_size=request.batch_size
    )
    
    return {
        "job_id": job.id,
        "status": job.status,
        "table_name": job.table_name,
        "cursor_column": job.cursor_column,
        "cursor_value": job.cursor_value,
        "total_records": job.total_records,
        "extracted_records": job.extracted_records,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }

@app.get("/extract/jobs", response_model=Dict[str, List[Dict[str, Any]]])
def get_extract_jobs():
    """List all extract jobs"""
    return list_jobs()

@app.get("/extract/jobs/{job_id}", response_model=Dict[str, Any])
def get_extract_job(job_id: str):
    """Get status of a specific extract job"""
    job = get_job_status(job_id)
    if job:
        return job
    else:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)