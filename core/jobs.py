import uuid
from datetime import datetime
from typing import Any, Optional, Dict
from dataclasses import dataclass, field, asdict

@dataclass
class ExtractJob:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    table_name: str = ""
    use_ctid: bool = True
    cursor_column: Optional[str] = None
    cursor_value: Any = None
    batch_size: int = 1000
    status: str = "pending"
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_records: int = 0
    extracted_records: int = 0
    celery_task_id: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class LoadJob:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    extract_job_id: str = ""
    destination_type: str = ""
    destination_config: Dict[str, Any] = field(default_factory=dict)
    dataset: str = ""
    table: str = ""
    status: str = "pending"
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    records_loaded: int = 0
    celery_task_id: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)