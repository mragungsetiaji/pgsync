from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, UniqueConstraint, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=5432)
    database = Column(String(100), nullable=False)
    user = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    extract_jobs = relationship("ExtractionJob", back_populates="source", cascade="all, delete-orphan")
    schema_versions = relationship("SchemaVersion", back_populates="source", cascade="all, delete-orphan")
    connections = relationship("Connection", back_populates="source")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
class SchemaVersion(Base):
    __tablename__ = "schema_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    schema = Column(JSON, nullable=False)  # The schema in JSON format
    hash = Column(String(64), nullable=False)  # Hash of the schema for quick comparison
    version = Column(Integer, nullable=False)  # Version number
    is_current = Column(Boolean, default=True)  # Whether this is the current schema
    created_at = Column(DateTime, server_default=func.now())

    source = relationship("Source", back_populates="schema_versions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "version": self.version,
            "is_current": self.is_current,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "schema": self.schema
        }
    
class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    table_name = Column(String(100), nullable=False)
    cursor_column = Column(String(100), nullable=False)
    cursor_value = Column(Text, nullable=True)
    batch_size = Column(Integer, default=1000)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    error = Column(Text, nullable=True)
    total_records = Column(Integer, default=0)
    extracted_records = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    source = relationship("Source", back_populates="extract_jobs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "table_name": self.table_name,
            "cursor_column": self.cursor_column,
            "cursor_value": self.cursor_value,
            "batch_size": self.batch_size,
            "status": self.status,
            "error": self.error,
            "total_records": self.total_records,
            "extracted_records": self.extracted_records,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
class SyncTable(Base):
    """Model to track which tables should be synced"""
    __tablename__ = "sync_tables"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    table_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    cursor_column = Column(String(100), nullable=False)  # Column to use for incremental syncing
    batch_size = Column(Integer, default=1000)
    sync_interval = Column(Integer, default=60)  # In minutes, how often to sync
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Ensure source_db_id + table_name is unique
    __table_args__ = (
        UniqueConstraint('source_id', 'table_name', name='uix_sync_table'),
    )
    
    # Relationships
    source = relationship("Source", backref="sync_tables")
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "table_name": self.table_name,
            "is_active": self.is_active,
            "cursor_column": self.cursor_column,
            "batch_size": self.batch_size,
            "sync_interval": self.sync_interval,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
class Destination(Base):
    """Model for storing destination configurations"""
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    
    project_id = Column(String(100), nullable=False)
    dataset = Column(String(100), nullable=False)
    credentials_json_base64 = Column(Text, nullable=False)

    bucket_name = Column(String(100), nullable=False)
    folder_path = Column(String(255), nullable=True)
    hmac_key = Column(String(255), nullable=False)
    hmac_secret = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    connections = relationship("Connection", back_populates="destination")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "dataset": self.dataset,
            "bucket_name": self.bucket_name,
            "folder_path": self.folder_path,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    
## Connection Settings
class ScheduleType(enum.Enum):
    MANUAL = "manual"
    CRON = "cron"

class Connection(Base):
    """Model for storing connections between sources and destinations"""
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, unique=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False)
    schedule_type = Column(Enum(ScheduleType), default=ScheduleType.MANUAL, nullable=False)
    cron_expression = Column(String(100), nullable=True)  # Only used when schedule_type is CRON
    timezone = Column(String(50), default="UTC", nullable=True)  # Timezone for CRON
    is_active = Column(Boolean, default=True)
    connection_state = Column(JSON, nullable=True)  # Any additional connection state info
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    celery_task_id = Column(String(50), nullable=True)  # Store Celery task ID for tracking
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    source = relationship("Source", back_populates="connections")
    destination = relationship("Destination", back_populates="connections")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "schedule_type": self.schedule_type.value,
            "cron_expression": self.cron_expression,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "connection_state": self.connection_state,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "celery_task_id": self.celery_task_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }