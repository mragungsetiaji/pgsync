import os
import json
import tempfile
from google.cloud import storage
from core.base import BaseLoader
from connector.bigquery_destination import BigQueryDestination

class BigQueryLoader(BaseLoader):
    """
    A class to load data into BigQuery, potentially via GCS staging.
    """
    def __init__(self, credentials):
        super().__init__(credentials)
        self.destination = BigQueryDestination(
            credentials_json=credentials.get("credentials_json"),
            credentials_path=credentials.get("credentials_path"),
            project_id=credentials.get("project_id")
        )
        self.use_gcs_staging = credentials.get("use_gcs_staging", False)
        self.gcs_bucket = credentials.get("gcs_bucket")
        self.gcs_path_prefix = credentials.get("gcs_path_prefix", "staging")
        
        if self.use_gcs_staging:
            self.gcs_client = storage.Client(
                credentials=self.destination.credentials,
                project=self.destination.project_id
            )
            self._validate_gcs_bucket()
    
    def _validate_credentials(self):
        """Validate the provided BigQuery credentials"""
        try:
            self.destination.check_connection()
        except Exception as e:
            self.logger.error(f"BigQuery credentials validation failed: {str(e)}")
            raise ValueError(f"BigQuery credentials validation failed: {str(e)}")
    
    def _validate_gcs_bucket(self):
        """Validate that the GCS bucket exists and is accessible"""
        if not self.use_gcs_staging:
            return
        
        if not self.gcs_bucket:
            raise ValueError("GCS bucket name is required for GCS staging")
        
        try:
            self.gcs_client.get_bucket(self.gcs_bucket)
        except Exception as e:
            self.logger.error(f"GCS bucket validation failed: {str(e)}")
            raise ValueError(f"GCS bucket validation failed: {str(e)}")
    
    def upload_to_gcs(self, data, table_name):
        """Upload JSON data to GCS"""
        if not self.use_gcs_staging:
            self.logger.warning("GCS staging not enabled, skipping GCS upload")
            return None
        
        try:
            bucket = self.gcs_client.bucket(self.gcs_bucket)
            timestamp = self._get_timestamp()
            blob_name = f"{self.gcs_path_prefix}/{table_name}/{timestamp}.json"
            blob = bucket.blob(blob_name)
            
            # Write data to temporary file, then upload
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp:
                json.dump(data, temp)
                temp_file_name = temp.name
            
            # Upload the file to GCS
            with open(temp_file_name, 'rb') as f:
                blob.upload_from_file(f)
            
            # Clean up the temporary file
            os.remove(temp_file_name)
            
            self.logger.info(f"Uploaded data to GCS: gs://{self.gcs_bucket}/{blob_name}")
            return f"gs://{self.gcs_bucket}/{blob_name}"
            
        except Exception as e:
            self.logger.error(f"Error uploading to GCS: {str(e)}")
            raise ValueError(f"Error uploading to GCS: {str(e)}")
    
    def load_to_bigquery(self, dataset_id, table_id, data=None, gcs_uri=None):
        """Load data into BigQuery, either directly or from GCS"""
        try:
            # Make sure the dataset exists
            self.destination.create_dataset(dataset_id)
            
            if gcs_uri:
                # Load from GCS
                job_config = self._create_load_job_config()
                load_job = self.destination.bq_client.load_table_from_uri(
                    gcs_uri,
                    f"{self.destination.project_id}.{dataset_id}.{table_id}",
                    job_config=job_config
                )
                load_job.result()  # Wait for the job to complete
                self.logger.info(f"Loaded data from {gcs_uri} to {dataset_id}.{table_id}")
            
            elif data:
                # Load directly from JSON data
                job_config = self._create_load_job_config()
                
                # Write data to temp file, then load
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp:
                    json.dump(data, temp)
                    temp_file_name = temp.name
                
                with open(temp_file_name, 'rb') as f:
                    load_job = self.destination.bq_client.load_table_from_file(
                        f,
                        f"{self.destination.project_id}.{dataset_id}.{table_id}",
                        job_config=job_config
                    )
                    load_job.result()  # Wait for the job to complete
                
                # Clean up the temporary file
                os.remove(temp_file_name)
                self.logger.info(f"Loaded {len(data)} records to {dataset_id}.{table_id}")
            
            else:
                raise ValueError("Either data or gcs_uri must be provided")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data to BigQuery: {str(e)}")
            raise ValueError(f"Error loading data to BigQuery: {str(e)}")
    
    def _create_load_job_config(self):
        """Create a job config for loading data"""
        job_config = self.destination.bq_client.LoadJobConfig()
        job_config.source_format = self.destination.bq_client.job.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.autodetect = True
        job_config.write_disposition = self.destination.bq_client.job.WriteDisposition.WRITE_APPEND
        return job_config
    
    def _get_timestamp(self):
        """Generate a timestamp string for use in file names"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")