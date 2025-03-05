from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class SourceDatabase(Base):
    __tablename__ = "source_databases"
    
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

    extract_jobs = relationship("ExtractionJob", back_populates="source_db", cascade="all, delete-orphan")
    schema_versions = relationship("SchemaVersion", back_populates="source_db", cascade="all, delete-orphan")
    
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
    source_db_id = Column(Integer, ForeignKey("source_databases.id"), nullable=False)
    schema = Column(JSON, nullable=False)  # The schema in JSON format
    hash = Column(String(64), nullable=False)  # Hash of the schema for quick comparison
    version = Column(Integer, nullable=False)  # Version number
    is_current = Column(Boolean, default=True)  # Whether this is the current schema
    created_at = Column(DateTime, server_default=func.now())

    source_db = relationship("SourceDatabase", back_populates="schema_versions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_db_id": self.source_db_id,
            "version": self.version,
            "is_current": self.is_current,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "schema": self.schema
        }
    
class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_db_id = Column(Integer, ForeignKey("source_databases.id"), nullable=False)
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
    
    source_db = relationship("SourceDatabase", back_populates="extract_jobs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_db_id": self.source_db_id,
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