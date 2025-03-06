import json
import os
import tempfile
from typing import Dict, List, Any, Optional
from google.cloud import storage, bigquery
from google.oauth2 import service_account
import pandas as pd
import uuid

class BigQueryDestination:
    """Service for handling data transfers to BigQuery via GCS"""
    
    def __init__(
        self,
        project_id: str,
        dataset: str,
        credentials: str,
        bucket_name: str,
        folder_path: Optional[str] = None,
        hmac_key: str = None,
        hmac_secret: str = None
    ):
        """
        Initialize BigQuery and GCS clients
        
        Args:
            project_id: Google Cloud project ID
            dataset: BigQuery dataset name
            credentials: JSON string with Google Cloud credentials
            bucket_name: GCS bucket name
            folder_path: Folder path within bucket (optional)
            hmac_key: HMAC key for GCS authentication
            hmac_secret: HMAC secret for GCS authentication
        """
        self.project_id = project_id
        self.dataset = dataset
        self.bucket_name = bucket_name
        self.folder_path = folder_path or ""
        
        # Parse credentials
        try:
            self.credentials_dict = json.loads(credentials)
            
            # Initialize using service account
            self.credentials = service_account.Credentials.from_service_account_info(
                self.credentials_dict
            )
            
            # Initialize BigQuery client
            self.bq_client = bigquery.Client(
                project=project_id,
                credentials=self.credentials
            )
            
            # Initialize GCS client
            if hmac_key and hmac_secret:
                # Use HMAC authentication for GCS
                self.storage_client = storage.Client(
                    project=project_id,
                    credentials=self.credentials
                )
                self.hmac_key = hmac_key
                self.hmac_secret = hmac_secret
            else:
                # Use service account for GCS
                self.storage_client = storage.Client(
                    project=project_id,
                    credentials=self.credentials
                )
                self.hmac_key = None
                self.hmac_secret = None
                
        except json.JSONDecodeError:
            raise ValueError("Invalid credentials JSON format")
        except Exception as e:
            raise ValueError(f"Error initializing BigQuery/GCS clients: {str(e)}")

    def _get_bucket(self):
        """Get GCS bucket object"""
        return self.storage_client.bucket(self.bucket_name)
        
    def check_connection(self) -> bool:
        """
        Check if the BigQuery and GCS connections are working
        
        Returns:
            bool: True if connections are successful, False otherwise
        """
        try:
            # Check BigQuery connection
            datasets = list(self.bq_client.list_datasets(max_results=1))
            
            # Check GCS connection
            bucket = self._get_bucket()
            blobs = list(bucket.list_blobs(max_results=1))
            
            return True
        except Exception as e:
            print(f"Connection check failed: {str(e)}")
            return False
            
    def check_dataset_exists(self) -> bool:
        """
        Check if the configured dataset exists
        
        Returns:
            bool: True if dataset exists, False otherwise
        """
        try:
            dataset_ref = self.bq_client.dataset(self.dataset)
            dataset = self.bq_client.get_dataset(dataset_ref)
            return True
        except Exception as e:
            print(f"Dataset check failed: {str(e)}")
            return False
    
    def upload_to_gcs(self, data: pd.DataFrame, table_name: str) -> str:
        """
        Upload data to GCS as CSV
        
        Args:
            data: Pandas DataFrame with data to upload
            table_name: Name of the destination table
            
        Returns:
            str: GCS URI of the uploaded file
        """
        try:
            # Create a unique filename
            unique_id = str(uuid.uuid4())
            timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
            filename = f"{table_name}_{timestamp}_{unique_id}.csv"
            
            # Construct the GCS path
            folder = self.folder_path.rstrip('/') if self.folder_path else ""
            if folder:
                blob_name = f"{folder}/{filename}"
            else:
                blob_name = filename
                
            # Get bucket
            bucket = self._get_bucket()
            blob = bucket.blob(blob_name)
            
            # Export dataframe to CSV in memory
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as temp_file:
                data.to_csv(temp_file.name, index=False)
                temp_file_path = temp_file.name
            
            # Upload file
            blob.upload_from_filename(temp_file_path)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Return GCS URI
            return f"gs://{self.bucket_name}/{blob_name}"
            
        except Exception as e:
            raise ValueError(f"Error uploading to GCS: {str(e)}")
    
    def create_table_if_not_exists(
        self, 
        table_name: str, 
        schema: List[Dict[str, Any]],
        partition_field: Optional[str] = None
    ) -> None:
        """
        Create a BigQuery table if it doesn't exist
        
        Args:
            table_name: Name of the table to create
            schema: List of column definitions
            partition_field: Field to use for partitioning (optional)
        """
        try:
            table_id = f"{self.project_id}.{self.dataset}.{table_name}"
            
            # Convert schema to BigQuery format
            bq_schema = []
            for field in schema:
                field_type = self._map_pg_type_to_bq(field["data_type"])
                bq_schema.append(
                    bigquery.SchemaField(
                        field["name"], 
                        field_type,
                        mode="NULLABLE" if field.get("nullable", True) else "REQUIRED"
                    )
                )
            
            # Set up table options
            table = bigquery.Table(table_id, schema=bq_schema)
            
            # Configure partitioning if requested
            if partition_field:
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field=partition_field
                )
            
            # Create the table if it doesn't exist
            table = self.bq_client.create_table(table, exists_ok=True)
            print(f"Created or retrieved table {table.table_id}")
            
        except Exception as e:
            raise ValueError(f"Error creating BigQuery table: {str(e)}")
    
    def _map_pg_type_to_bq(self, pg_type: str) -> str:
        """
        Map PostgreSQL data type to BigQuery data type
        
        Args:
            pg_type: PostgreSQL data type
            
        Returns:
            str: Equivalent BigQuery data type
        """
        # Basic type mapping
        type_mapping = {
            "integer": "INT64",
            "bigint": "INT64",
            "smallint": "INT64",
            "int": "INT64",
            "int2": "INT64", 
            "int4": "INT64",
            "int8": "INT64",
            "numeric": "NUMERIC",
            "decimal": "NUMERIC",
            "real": "FLOAT64",
            "float": "FLOAT64",
            "double precision": "FLOAT64",
            "float4": "FLOAT64",
            "float8": "FLOAT64",
            "boolean": "BOOL",
            "bool": "BOOL",
            "varchar": "STRING",
            "character varying": "STRING",
            "char": "STRING",
            "text": "STRING",
            "date": "DATE",
            "timestamp": "TIMESTAMP",
            "timestamp without time zone": "TIMESTAMP",
            "timestamp with time zone": "TIMESTAMP",
            "timestamptz": "TIMESTAMP",
            "time": "TIME",
            "time without time zone": "TIME",
            "time with time zone": "TIME",
            "json": "JSON",
            "jsonb": "JSON",
            "uuid": "STRING",
            "bytea": "BYTES",
            "array": "ARRAY"
        }
        
        # Handle array types
        if pg_type.startswith("_"):
            base_type = pg_type[1:]
            bq_base_type = self._map_pg_type_to_bq(base_type)
            return f"ARRAY<{bq_base_type}>"
            
        # Check if type is in mapping
        lowered = pg_type.lower()
        for pg_pattern, bq_type in type_mapping.items():
            if pg_pattern in lowered:
                return bq_type
        
        # Default to STRING for unknown types
        return "STRING"
    
    def load_from_gcs_to_bigquery(
        self, 
        gcs_uri: str, 
        table_name: str,
        write_disposition: str = "WRITE_APPEND"
    ) -> None:
        """
        Load data from GCS to BigQuery
        
        Args:
            gcs_uri: GCS URI of the file to load
            table_name: Destination table name
            write_disposition: How to handle existing data (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
        """
        try:
            # Configure job
            table_id = f"{self.project_id}.{self.dataset}.{table_name}"
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition=write_disposition
            )
            
            # Start load job
            load_job = self.bq_client.load_table_from_uri(
                gcs_uri, table_id, job_config=job_config
            )
            
            # Wait for job to complete
            load_job.result()
            
            # Get loaded table
            table = self.bq_client.get_table(table_id)
            print(f"Loaded {table.num_rows} rows to {table_id}")
            
        except Exception as e:
            raise ValueError(f"Error loading data to BigQuery: {str(e)}")
    
    def sync_data(
        self,
        data: pd.DataFrame,
        table_name: str,
        schema: List[Dict[str, Any]],
        write_disposition: str = "WRITE_APPEND",
        partition_field: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync data to BigQuery (upload to GCS and then load to BigQuery)
        
        Args:
            data: Pandas DataFrame with data to sync
            table_name: Destination table name
            schema: Table schema information
            write_disposition: How to handle existing data
            partition_field: Field to use for partitioning (optional)
            
        Returns:
            Dict[str, Any]: Sync operation result
        """
        try:
            # Create table if it doesn't exist
            self.create_table_if_not_exists(table_name, schema, partition_field)
            
            # Upload data to GCS
            gcs_uri = self.upload_to_gcs(data, table_name)
            
            # Load data from GCS to BigQuery
            self.load_from_gcs_to_bigquery(gcs_uri, table_name, write_disposition)
            
            return {
                "status": "success",
                "rows_synced": len(data),
                "gcs_uri": gcs_uri,
                "table": f"{self.project_id}.{self.dataset}.{table_name}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }