import asyncio
import logging
import os
import glob
import json
from datetime import datetime, timezone

from worker.celery_app import celery_app
from worker.job_manager import update_job_status, get_job_status
from core.jobs import ExtractJob, LoadJob
from connector.postgres_extractor import PostgresExtractor
from connector.transformer import Transformer
from connector.bigquery_loader import BigQueryLoader

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

@celery_app.task(name="transform.process_data", bind=True)
def process_transform_task(self, extract_job_id, generation_id=None):
    """Transform extracted data into Airbyte format"""
    task_id = self.request.id
    
    # Get extract job details
    extract_job_data = get_job_status(extract_job_id)
    if not extract_job_data or extract_job_data.get('status') != 'completed':
        logger.error(f"Cannot transform data for extract job {extract_job_id} - job not completed")
        return False
    
    # Create transformer
    transformer = Transformer(generation_id)
    
    # Find all output files for this job
    output_dir = os.path.join(os.getcwd(), "data", "output")
    pattern = f"{extract_job_data['table_name']}_{extract_job_id}_*_*.json"
    batch_files = glob.glob(os.path.join(output_dir, pattern))
    
    if not batch_files:
        logger.error(f"No batch files found for extract job {extract_job_id}")
        return False
    
    # Transform each batch and save to transformed directory
    transform_dir = os.path.join(os.getcwd(), "data", "transformed")
    os.makedirs(transform_dir, exist_ok=True)
    
    total_transformed = 0
    transformed_files = []

    for batch_file in batch_files:
        try:
            # Transform the batch
            transformed_data = transformer.transform_batch_from_file(batch_file)
            total_transformed += len(transformed_data)
            
            # Save the transformed batch
            filename = os.path.basename(batch_file).replace('.json', '_transformed.json')
            transform_path = os.path.join(transform_dir, filename)
            
            with open(transform_path, 'w') as f:
                json.dump(transformed_data, f)
                
            transformed_files.append(transform_path)
            logger.info(f"Transformed batch saved to {transform_path}")
            
        except Exception as e:
            logger.error(f"Error transforming batch {batch_file}: {str(e)}")
            return False
    
    logger.info(f"Successfully transformed {total_transformed} records across {len(batch_files)} batches")
    return {
        "extract_job_id": extract_job_id,
        "transformed_files": transformed_files,
        "total_transformed": total_transformed,
        "generation_id": transformer.generation_id
    }

@celery_app.task(name="load.process_data", bind=True)
def process_load_task(self, load_job_dict, transform_result):
    """Load transformed data into destination"""
    task_id = self.request.id
    job = LoadJob(**load_job_dict)
    job.celery_task_id = task_id
    job.status = "running"
    job.updated_at = datetime.now().isoformat()
    update_job_status(job)
    
    try:
        # Get the destination configuration
        if job.destination_type.lower() != "bigquery":
            job.status = "failed"
            job.error = f"Unsupported destination type: {job.destination_type}"
            job.updated_at = datetime.now().isoformat()
            update_job_status(job)
            return False
            
        # Initialize the loader
        loader = BigQueryLoader(job.destination_config)
        
        # Process each transformed file
        total_loaded = 0
        for file_path in transform_result["transformed_files"]:
            # Load the transformed data
            with open(file_path, 'r') as f:
                transformed_data = json.load(f)
                
            # Add loading timestamp to the records
            loaded_at = datetime.now(timezone.utc).isoformat()
            for record in transformed_data:
                record["_airbyte_loaded_at"] = loaded_at
                
            # Load the data to BigQuery
            loader.load_to_bigquery(job.dataset, job.table, transformed_data)
            total_loaded += len(transformed_data)
            
            # Update job status
            job.records_loaded += len(transformed_data)
            job.updated_at = datetime.now().isoformat()
            update_job_status(job)
        
        # Mark job as completed
        job.status = "completed"
        job.updated_at = datetime.now().isoformat()
        update_job_status(job)
        logger.info(f"Successfully loaded {total_loaded} records to {job.dataset}.{job.table}")
        return True
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        job.status = "failed"
        job.error = str(e)
        job.updated_at = datetime.now().isoformat()
        update_job_status(job)
        return False
    
def add_load_job(extract_job_id, destination_type, destination_config, dataset, table):
    """Create and queue a load job"""
    # First transform the data
    transform_result = process_transform_task.delay(extract_job_id)
    transform_result = transform_result.get()  # Wait for transform to complete
    
    if not transform_result:
        logger.error(f"Transform failed for extract job {extract_job_id}")
        return None
    
    # Create load job
    job = LoadJob(
        extract_job_id=extract_job_id,
        destination_type=destination_type,
        destination_config=destination_config,
        dataset=dataset,
        table=table
    )
    
    # Queue the load job
    job_dict = job.to_dict()
    result = process_load_task.delay(job_dict, transform_result)
    job.celery_task_id = result.id
    update_job_status(job)
    
    logger.info(f"Added load job {job.id} to Celery queue for {dataset}.{table}")
    return job