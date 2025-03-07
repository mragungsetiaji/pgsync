import asyncio
import logging
from datetime import datetime

from worker.celery_app import celery_app
from worker.job_manager import update_job_status
from core.jobs import ExtractJob
from connector.postgres_extractor import PostgresExtractor

logger = logging.getLogger("extract.tasks")

@celery_app.task(name="extract.process_job", bind=True)
def process_job_task(self, job_dict, conn_params):
    task_id = self.request.id
    job_dict['celery_task_id'] = task_id
    job_dict['status'] = 'running'
    job_dict['updated_at'] = datetime.now().isoformat()
    update_job_status(ExtractJob(**job_dict))
    extractor = PostgresExtractor(conn_params)
    result = asyncio.run(extractor.extract_incremental(job_dict))
    return result

def add_extract_job(source_db_id, table_name, use_ctid=True, cursor_column=None, cursor_value=None, batch_size=1000, conn_params=None):
    job = ExtractJob(
        table_name=table_name,
        use_ctid=use_ctid,
        cursor_column=cursor_column if not use_ctid else None,
        cursor_value=cursor_value,
        batch_size=batch_size
    )
    job_dict = job.to_dict()
    result = process_job_task.delay(job_dict, conn_params)
    job.celery_task_id = result.id
    update_job_status(job)
    logger.info(f"Added job {job.id} to Celery queue for table {table_name}")
    return job