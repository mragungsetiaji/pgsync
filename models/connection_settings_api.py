from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class ScheduleTypeEnum(str, Enum):
    """API enum for schedule types"""
    MANUAL = "manual"
    CRON = "cron"

class ConnectionSettingsCreate(BaseModel):
    """Model for creating connection settings"""
    name: str = Field(..., min_length=1, max_length=100)
    schedule_type: ScheduleTypeEnum = ScheduleTypeEnum.MANUAL
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    is_active: bool = True
    connection_state: Optional[Dict[str, Any]] = None
    
    @field_validator('cron_expression')
    def validate_cron_expression(cls, value, values):
        # If schedule type is CRON, cron_expression is required
        if values.get('schedule_type') == ScheduleTypeEnum.CRON and not value:
            raise ValueError("Cron expression is required when schedule type is 'cron'")
        
        # Basic cron expression validation (very simplified)
        if value:
            parts = value.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts (minute, hour, day of month, month, day of week)")
        
        return value

class ConnectionSettingsUpdate(BaseModel):
    """Model for updating connection settings"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    schedule_type: Optional[ScheduleTypeEnum] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    connection_state: Optional[Dict[str, Any]] = None
    
    @field_validator('cron_expression')
    def validate_cron_expression(cls, value, values):
        # Only validate if value is not None
        if value is not None and values.get('schedule_type') == ScheduleTypeEnum.CRON:
            parts = value.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts (minute, hour, day of month, month, day of week)")
        
        return value

class ConnectionSettingsResponse(BaseModel):
    """Response model for connection settings"""
    id: int
    name: str
    schedule_type: str
    cron_expression: Optional[str]
    timezone: str
    is_active: bool
    connection_state: Optional[Dict[str, Any]]
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]