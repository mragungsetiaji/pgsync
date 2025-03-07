from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from models.database import ScheduleType

class DestinationCreate(BaseModel):
    """Model for creating destination"""
    name: str = Field(..., min_length=1, max_length=100)
    project_id: str
    dataset: str
    credentials: str  # JSON string with credentials
    bucket_name: str
    folder_path: Optional[str] = None
    hmac_key: str
    hmac_secret: str
    is_active: bool = True

class DestinationUpdate(BaseModel):
    """Model for updating destination"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    project_id: Optional[str] = None
    dataset: Optional[str] = None
    credentials: Optional[str] = None
    bucket_name: Optional[str] = None
    folder_path: Optional[str] = None
    hmac_key: Optional[str] = None
    hmac_secret: Optional[str] = None
    is_active: Optional[bool] = None

class DestinationResponse(BaseModel):
    """Response model for destination"""
    id: int
    name: str
    type: str
    project_id: str
    dataset: str
    bucket_name: str
    folder_path: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ConnectionCreate(BaseModel):
    """Model for creating connection between source and destination"""
    name: str = Field(..., min_length=1, max_length=100) 
    source_db_id: int
    destination_id: int
    schedule_type: ScheduleType = ScheduleType.MANUAL
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    is_active: bool = True
    connection_state: Optional[Dict[str, Any]] = None
    
    @field_validator('cron_expression')
    def validate_cron_expression(cls, value, values):
        # If schedule type is CRON, cron_expression is required
        if values.get('schedule_type') == ScheduleType.CRON and not value:
            raise ValueError("Cron expression is required when schedule type is 'cron'")
        
        # Basic cron expression validation (very simplified)
        if value:
            parts = value.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts (minute, hour, day of month, month, day of week)")
        
        return value

class ConnectionUpdate(BaseModel):
    """Model for updating connection"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_db_id: Optional[int] = None
    destination_id: Optional[int] = None
    schedule_type: Optional[ScheduleType] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    connection_state: Optional[Dict[str, Any]] = None
    
    @field_validator('cron_expression')
    def validate_cron_expression(cls, value, values):
        if value is not None and values.get('schedule_type') == ScheduleType.CRON:
            parts = value.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts (minute, hour, day of month, month, day of week)")
        return value

class ConnectionResponse(BaseModel):
    """Response model for connection"""
    id: int
    name: str
    source_db_id: int
    source_db_name: str
    destination_id: int
    destination_name: str
    schedule_type: str
    cron_expression: Optional[str]
    timezone: str
    is_active: bool
    connection_state: Optional[Dict[str, Any]]
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    created_at: str
    updated_at: str

class TestBigQueryConnectionRequest(BaseModel):
    """Request model for testing BigQuery connection"""
    project_id: str
    dataset: str
    credentials: str
    bucket_name: str
    folder_path: Optional[str] = None
    hmac_key: str
    hmac_secret: str