from fastapi import FastAPI
from models.api import StatusResponse
from route.sources import router as sources_router
from route.extractions import router as extractions_router
from route.sync_tables import router as sync_tables_router

app = FastAPI(
    title="PostgreSQL Database Explorer",
    description="API to explore PostgreSQL database structure and execute queries",
    version="1.0.0",
)

# Register routers
app.include_router(sources_router)
app.include_router(extractions_router)
app.include_router(sync_tables_router)

@app.get("/", response_model=StatusResponse)
def root():
    """Health check endpoint"""
    return {"status": "success", "message": "PostgreSQL API is running"}

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Run PGSync server or worker")
    parser.add_argument("--mode",
                        type=str, 
                        choices=["server", "worker"], 
                        default="server", 
                        help="Run mode: 'server' for API or 'worker' for Celery")
    parser.add_argument("--loglevel", 
                        type=str, 
                        default="info", 
                        help="Log level for Celery worker")
    parser.add_argument("--concurrency", 
                        type=int, 
                        default=None, 
                        help="Number of worker processes/threads")
    
    args = parser.parse_args()
    
    if args.mode == "server":

        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    elif args.mode == "worker":

        from pipeline.extract import celery_app
        worker_args = ["worker", f"--loglevel={args.loglevel}"]
        if args.concurrency:
            worker_args.append(f"--concurrency={args.concurrency}")
            
        celery_app.worker_main(worker_args)