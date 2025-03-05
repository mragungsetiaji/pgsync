from contextlib import asynccontextmanager
from fastapi import FastAPI
from models.api import StatusResponse
from config import (
    PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
)

from pipeline.extract import start_worker
from route.sources import router as sources_router
from route.extractions import router as extractions_router

app = FastAPI(
    title="PostgreSQL Database Explorer",
    description="API to explore PostgreSQL database structure and execute queries",
    version="1.0.0"
)

# Register routers
app.include_router(sources_router)
app.include_router(extractions_router)

# Start worker process when app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Get database connection info from environment variables
    conn_params = {
        "host": PG_HOST,
        "port": PG_PORT,
        "dbname": PG_DATABASE,
        "user": PG_USER,
        "password": PG_PASSWORD
    }
    start_worker(conn_params)

@app.get("/", response_model=StatusResponse)
def root():
    """Health check endpoint"""
    return {"status": "success", "message": "PostgreSQL API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)