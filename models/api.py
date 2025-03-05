from pydantic import BaseModel, Field
from typing import Optional, List, Any

# Models for request and response
class ConnectionInfo(BaseModel):
    host: str
    port: int = 5432
    database: str
    user: str
    password: str

class QueryRequest(BaseModel):
    query: str
    params: Optional[List[Any]] = None

class StatusResponse(BaseModel):
    status: str
    message: str

class ExtractRequest(BaseModel):
    """Request model for incremental data extract"""
    table_name: str
    cursor_column: str
    cursor_value: Optional[Any] = None
    batch_size: int = 1000

class JobResponse(BaseModel):
    """Response model for job information"""
    job_id: str
    status: str
    table_name: str
    cursor_column: str
    cursor_value: Any
    total_records: int
    extracted_records: int
    created_at: str
    updated_at: str

# Source database models
class SourceDatabaseCreate(BaseModel):
    name: str
    host: str
    port: int = 5432
    database: str
    user: str
    password: str

class SourceDatabaseUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class SourceDatabaseResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    database: str
    user: str
    is_active: bool
    created_at: str
    updated_at: str

# Extraction job models
class ExtractJobCreate(BaseModel):
    source_db_id: int
    table_name: str
    cursor_column: str
    cursor_value: Optional[Any] = None
    batch_size: int = 1000

class ExtractJobResponse(BaseModel):
    id: str
    source_db_id: int
    table_name: str
    cursor_column: str
    cursor_value: Optional[Any] = None
    batch_size: int
    status: str
    error: Optional[str] = None
    total_records: int
    extracted_records: int
    created_at: str
    updated_at: str

# Testing connection
class TestConnectionRequest(BaseModel):
    host: str
    port: int = 5432
    database: str
    user: str
    password: str

# General responses
class StatusResponse(BaseModel):
    status: str
    message: str

# sync-tables
class SyncTableCreate(BaseModel):
    source_db_id: int
    table_name: str
    cursor_column: str
    is_active: bool = True
    batch_size: int = Field(1000, ge=100, le=10000)
    sync_interval: int = Field(60, ge=5, le=1440)  # 5 min to 24 hours

class SyncTableUpdate(BaseModel):
    is_active: Optional[bool] = None
    cursor_column: Optional[str] = None
    batch_size: Optional[int] = Field(None, ge=100, le=10000)
    sync_interval: Optional[int] = Field(None, ge=5, le=1440)

class SyncTableResponse(BaseModel):
    id: int
    source_db_id: int
    source_db_name: str
    table_name: str
    is_active: bool
    cursor_column: str
    batch_size: int
    sync_interval: int
    last_synced_at: Optional[str] = None
    created_at: str
    updated_at: str
