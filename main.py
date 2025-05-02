from fastapi import FastAPI
from models.api import StatusResponse
from route.sources import router as sources_router
from route.extractions import router as extractions_router
from route.sync_tables import router as sync_tables_router
from route.connections import router as connections_router
from route.destinations import router as destinations_router
from route.jobs import router as jobs_router
from sqlalchemy import text
from session_manager import engine, get_db_session
from worker.redis_client import RedisClient
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
import logging
import sys

# Configure logger
logger = logging.getLogger("pgsync")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI(
    title="PostgreSQL Database Explorer",
    description="API to explore PostgreSQL database structure and execute queries",
    version="1.0.0",
)

# Register routers
app.include_router(sources_router)
app.include_router(extractions_router)
app.include_router(sync_tables_router)
app.include_router(connections_router)
app.include_router(destinations_router)
app.include_router(jobs_router)

@app.get("/", response_model=StatusResponse)
def root():
    """Health check endpoint"""
    return {"status": "success", "message": "PostgreSQL API is running"}

def check_postgres_connection():
    """Verify PostgreSQL connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {str(e)}")
        return False
    
def check_redis_connection():
    """Verify Redis connection"""
    try:
        redis_client = RedisClient(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD
        )
        redis_client.client.ping()
        logger.info("✅ Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {str(e)}")
        return False
    
def verify_connections():
    """Verify all required connections"""
    pg_ok = check_postgres_connection()
    redis_ok = check_redis_connection()
    
    if not pg_ok or not redis_ok:
        logger.error("Critical services connection check failed. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Run PGSync server or worker")
    parser.add_argument("--mode",
                        type=str, 
                        choices=["server", "worker", "scheduler"], 
                        default="server", 
                        help="Run mode: 'server' for API or 'worker' for Celery or 'scheduler' for task scheduler")
    parser.add_argument("--loglevel", 
                        type=str, 
                        default="info", 
                        help="Log level for Celery worker")
    parser.add_argument("--concurrency", 
                        type=int, 
                        default=None, 
                        help="Number of worker processes/threads")
    parser.add_argument("--check-interval", type=int, default=60,
                       help="Interval in seconds to check for scheduled tasks (scheduler mode only)")
    
    args = parser.parse_args()
    
    if args.mode == "server":
        # Verify connections before starting server
        logger.info("Checking connections to required services...")
        verify_connections()
        logger.info("All connections verified. Starting API server...")

        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    elif args.mode == "worker":

        from worker.celery_app import celery_app
        worker_args = ["worker", f"--loglevel={args.loglevel}"]
        if args.concurrency:
            worker_args.append(f"--concurrency={args.concurrency}")
            
        celery_app.worker_main(worker_args)

    elif args.mode == "scheduler":
        
        from scheduler import run_scheduler
        run_scheduler(args)