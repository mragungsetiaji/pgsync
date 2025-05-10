from google.cloud import bigquery
from google.oauth2 import service_account
import base64
import json
import logging

class BigQueryDestination:
    """
    A class to handle BigQuery connection and schema operations.
    """
    def __init__(
            self, 
            project_id, 
            dataset,
            credentials_json_base64 
            ):
        """
        Initialize BigQuery connection parameters.
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account JSON as string
            project_id: Google Cloud project ID
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if credentials_json_base64:
            decoded_json = base64.b64decode(credentials_json_base64).decode('utf-8')
            credentials_dict = json.loads(decoded_json)
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict
            )
            self.project_id = credentials_dict.get("project_id")
        else:
            self.credentials = None
            self.project_id = project_id
        
        # Override project_id if explicitly provided
        if project_id:
            self.project_id = project_id
            
        self.bq_client = bigquery.Client(
            credentials=self.credentials,
            project=self.project_id
        )
        self.dataset = dataset
    
    def _get_project_id_from_credentials(self, credentials_path):
        """Extract project_id from service account JSON file"""
        try:
            with open(credentials_path, 'r') as f:
                credentials_dict = json.load(f)
                return credentials_dict.get('project_id')
        except Exception as e:
            self.logger.error(f"Error reading project_id from credentials: {str(e)}")
            return None
    
    def check_connection(self):
        """Test BigQuery connection by listing datasets"""
        try:
            # Try to list datasets as a connection test
            list(self.bq_client.list_datasets(max_results=1))
            return True
        except Exception as e:
            self.logger.error(f"BigQuery connection failed: {str(e)}")
            raise ValueError(f"BigQuery connection failed: {str(e)}")
    
    def list_datasets(self):
        """List all datasets in the project"""
        try:
            datasets = list(self.bq_client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            self.logger.error(f"Error listing datasets: {str(e)}")
            raise ValueError(f"Error listing datasets: {str(e)}")
    
    def list_tables(self, dataset_id):
        """List all tables in a dataset"""
        try:
            tables = list(self.bq_client.list_tables(f"{self.project_id}.{dataset_id}"))
            return [table.table_id for table in tables]
        except Exception as e:
            self.logger.error(f"Error listing tables: {str(e)}")
            raise ValueError(f"Error listing tables in dataset {dataset_id}: {str(e)}")
    
    def get_table_schema(self, dataset_id, table_id):
        """Get schema of a specific table"""
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            table = self.bq_client.get_table(table_ref)
            schema = []
            for field in table.schema:
                schema.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                })
            return schema
        except Exception as e:
            self.logger.error(f"Error getting table schema: {str(e)}")
            raise ValueError(f"Error getting schema for {dataset_id}.{table_id}: {str(e)}")
    
    def create_dataset(self, dataset_id, location="US"):
        """Create a new dataset in BigQuery"""
        try:
            dataset = bigquery.Dataset(f"{self.project_id}.{dataset_id}")
            dataset.location = location
            self.bq_client.create_dataset(dataset, exists_ok=True)
            self.logger.info(f"Dataset {dataset_id} created or already exists")
            return True
        except Exception as e:
            self.logger.error(f"Error creating dataset: {str(e)}")
            raise ValueError(f"Error creating dataset {dataset_id}: {str(e)}")
    
    def create_table(self, dataset_id, table_id, schema_fields, partition_field=None):
        """Create a new table in BigQuery with the given schema"""
        try:
            table_id_full = f"{self.project_id}.{dataset_id}.{table_id}"
            
            # Create BigQuery schema
            bq_schema = []
            for field in schema_fields:
                bq_schema.append(
                    bigquery.SchemaField(
                        name=field["name"],
                        field_type=self._map_pg_type_to_bq(field["type"]),
                        mode="NULLABLE" if field.get("nullable", True) else "REQUIRED"
                    )
                )
            
            # Set up table options
            table = bigquery.Table(table_id_full, schema=bq_schema)
            
            # Configure partitioning if requested
            if partition_field:
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field=partition_field
                )
            
            # Create the table if it doesn't exist
            table = self.bq_client.create_table(table, exists_ok=True)
            self.logger.info(f"Created or retrieved table {table.table_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating BigQuery table: {str(e)}")
            raise ValueError(f"Error creating BigQuery table: {str(e)}")
    
    def _map_pg_type_to_bq(self, pg_type: str) -> str:
        """Map PostgreSQL data type to BigQuery data type"""
        type_mapping = {
            "int2": "INTEGER",
            "int4": "INTEGER",
            "int8": "INTEGER",
            "smallint": "INTEGER",
            "integer": "INTEGER",
            "bigint": "INTEGER",
            "decimal": "NUMERIC",
            "numeric": "NUMERIC",
            "real": "FLOAT",
            "float4": "FLOAT",
            "float8": "FLOAT",
            "double precision": "FLOAT",
            "boolean": "BOOLEAN",
            "bool": "BOOLEAN",
            "varchar": "STRING",
            "character varying": "STRING",
            "char": "STRING",
            "text": "STRING",
            "json": "JSON",
            "jsonb": "JSON",
            "date": "DATE",
            "timestamp": "TIMESTAMP",
            "timestamptz": "TIMESTAMP",
            "timestamp with time zone": "TIMESTAMP",
            "timestamp without time zone": "TIMESTAMP",
            "time": "TIME",
            "timetz": "STRING",  # BigQuery has no TIME WITH TIMEZONE
            "time with time zone": "STRING",
            "bytea": "BYTES",
            "uuid": "STRING",
            "inet": "STRING",
            "macaddr": "STRING",
            "cidr": "STRING",
            # Add other mappings as needed
        }
        
        # Look for the type in the mapping
        # Use lowercase for comparison to handle case variations
        pg_type_lower = pg_type.lower()
        
        # Handle varchar(n) and similar types
        if "(" in pg_type_lower:
            base_type = pg_type_lower.split("(")[0].strip()
            return type_mapping.get(base_type, "STRING")
        
        return type_mapping.get(pg_type_lower, "STRING")  # Default to STRING for unknown types