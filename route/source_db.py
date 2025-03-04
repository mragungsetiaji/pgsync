from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.database import SourceDatabase
from session_manager import get_db_session
from models.api import (
    SourceDatabaseCreate, 
    SourceDatabaseUpdate, 
    SourceDatabaseResponse,
    TestConnectionRequest,
    StatusResponse
)
from source.postgres import Postgres

router = APIRouter(
    prefix="/sources",
    tags=["Source Databases"]
)

@router.post("/", response_model=SourceDatabaseResponse)
def create_source_db(db_data: SourceDatabaseCreate, db: Session = Depends(get_db_session)):
    """Create a new source database connection"""
    # Test the connection first
    postgres = Postgres(
        host=db_data.host,
        port=db_data.port,
        database=db_data.database,
        user=db_data.user,
        password=db_data.password
    )
    
    if not postgres.check_connection():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to the database with the provided credentials"
        )
    
    # Create the database entry
    db_obj = SourceDatabase(
        name=db_data.name,
        host=db_data.host,
        port=db_data.port,
        database=db_data.database,
        user=db_data.user,
        password=db_data.password
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj.to_dict()

@router.get("/", response_model=List[SourceDatabaseResponse])
def get_source_dbs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """Get all source database connections"""
    sources = db.query(SourceDatabase).offset(skip).limit(limit).all()
    return [source.to_dict() for source in sources]

@router.get("/{source_id}", response_model=SourceDatabaseResponse)
def get_source_db(source_id: int, db: Session = Depends(get_db_session)):
    """Get a specific source database connection"""
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    return db_obj.to_dict()

@router.put("/{source_id}", response_model=SourceDatabaseResponse)
def update_source_db(source_id: int, db_data: SourceDatabaseUpdate, db: Session = Depends(get_db_session)):
    """Update a source database connection"""
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    # Update attributes that were provided
    update_data = db_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    
    db.commit()
    db.refresh(db_obj)
    
    return db_obj.to_dict()

@router.delete("/{source_id}", response_model=StatusResponse)
def delete_source_db(source_id: int, db: Session = Depends(get_db_session)):
    """Delete a source database connection"""
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    db.delete(db_obj)
    db.commit()
    
    return {"status": "success", "message": f"Source database with ID {source_id} deleted successfully"}

@router.post("/test-connection", response_model=StatusResponse)
def test_connection(conn_data: TestConnectionRequest):
    """Test a database connection without saving it"""
    postgres = Postgres(
        host=conn_data.host,
        port=conn_data.port,
        database=conn_data.database,
        user=conn_data.user,
        password=conn_data.password
    )
    
    if postgres.check_connection():
        return {"status": "success", "message": "Connection successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to the database with the provided credentials"
        )

@router.get("/{source_id}/tables", response_model=List[str])
def get_source_tables(source_id: int, db: Session = Depends(get_db_session)):
    """Get all tables from a source database"""
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    postgres = Postgres(
        host=db_obj.host,
        port=db_obj.port,
        database=db_obj.database,
        user=db_obj.user,
        password=db_obj.password
    )
    
    tables = postgres.fetch_tables()
    return tables

@router.get("/{source_id}/tables/{table_name}/columns")
def get_source_table_columns(source_id: int, table_name: str, db: Session = Depends(get_db_session)):
    """Get columns for a specific table in a source database"""
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    postgres = Postgres(
        host=db_obj.host,
        port=db_obj.port,
        database=db_obj.database,
        user=db_obj.user,
        password=db_obj.password
    )
    
    columns = postgres.fetch_columns(table_name)
    if not columns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found in source database"
        )
    
    return columns