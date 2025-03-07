import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from core.base import BaseTransformer

class Transformer(BaseTransformer):
    """
    Transforms extracted data into raw format.
    
    The raw format includes these fields:
    - _raw_id: UUID for the record
    - _extracted_at: Timestamp when data was extracted
    - _loaded_at: Timestamp when data was loaded (initially null)
    - _data: JSON string containing the raw record data
    - _meta: Additional metadata (optional)
    - _generation_id: Generation identifier for this sync
    """
    
    def __init__(self, generation_id: Optional[str] = None):
        super().__init__()
        self.generation_id = generation_id or str(uuid.uuid4())
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a list of records into raw format.
        
        Args:
            data: List of records to transform
            
        Returns:
            List of transformed records in raw format
        """
        transformed_data = []
        extracted_at = datetime.now(timezone.utc).isoformat()
        
        for record in data:
            transformed_record = {
                "_raw_id": str(uuid.uuid4()),
                "_extracted_at": extracted_at,
                "_loaded_at": None,  # Will be set during load
                "_data": json.dumps(record),  # Store original record as JSON string
                "_meta": json.dumps({"source_timestamp": extracted_at}),
                "_generation_id": self.generation_id
            }
            transformed_data.append(transformed_record)
            
        self.logger.info(f"Transformed {len(data)} records into Airbyte format")
        return transformed_data
    
    def transform_batch_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read a batch file and transform its contents into raw format.
        
        Args:
            file_path: Path to the JSON file containing records
            
        Returns:
            List of transformed records in raw format
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            return self.transform(data)
        except Exception as e:
            self.logger.error(f"Error transforming batch from file {file_path}: {str(e)}")
            raise ValueError(f"Error transforming batch file: {str(e)}")
        
    def transform_batches(self, batches: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Transform multiple batches of data.
        
        Args:
            batches: List of data batches, where each batch is a list of records
            
        Returns:
            List of all transformed records
        """
        all_transformed = []
        for batch in batches:
            transformed_batch = self.transform(batch)
            all_transformed.extend(transformed_batch)
            
        self.logger.info(f"Transformed {len(all_transformed)} records from {len(batches)} batches")
        return all_transformed