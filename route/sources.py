import json
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc

from models.database import SourceDatabase, SchemaVersion
from session_manager import get_db_session
from models.api import (
    SourceDatabaseCreate, 
    SourceDatabaseUpdate, 
    SourceDatabaseResponse,
    TestConnectionRequest,
    StatusResponse
)
from services.postgres import Postgres

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

@router.post("/{source_id}/schema", response_model=StatusResponse)
def fetch_and_store_schema(source_id: int, db: Session = Depends(get_db_session)):
    """Fetch the schema from a source database and store it as a new version"""
    # Get source database
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    # Initialize Postgres connection
    postgres = Postgres(
        host=db_obj.host,
        port=db_obj.port,
        database=db_obj.database,
        user=db_obj.user,
        password=db_obj.password
    )

    # Fetch schema
    try:
        schema = postgres.fetch_schema()
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch database schema"
            )
        
        # Calculate schema hash for comparison
        schema_json = json.dumps(schema, sort_keys=True)
        schema_hash = hashlib.sha256(schema_json.encode()).hexdigest()
        
        # Check if schema has changed
        latest_schema = db.query(SchemaVersion).filter(
            SchemaVersion.source_db_id == source_id,
            SchemaVersion.is_current == True
        ).first()
        
        if latest_schema and latest_schema.hash == schema_hash:
            return {
                "status": "success", 
                "message": f"Schema for database '{db_obj.name}' is already up to date (version {latest_schema.version})"
            }
        
        # Get next version number
        next_version = 1
        if latest_schema:
            next_version = latest_schema.version + 1
            
            # Update all existing versions to not be current
            db.query(SchemaVersion).filter(
                SchemaVersion.source_db_id == source_id,
                SchemaVersion.is_current == True
            ).update({"is_current": False})

        # Create new schema version
        new_schema = SchemaVersion(
            source_db_id=source_id,
            schema=schema,
            hash=schema_hash,
            version=next_version,
            is_current=True
        )
        
        db.add(new_schema)
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Schema for database '{db_obj.name}' fetched and stored as version {next_version}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching schema: {str(e)}"
        )
    
@router.get("/{source_id}/schema", response_model=dict)
def get_source_schema(
    source_id: int, 
    version: Optional[int] = None,
    refresh: bool = False, 
    db: Session = Depends(get_db_session)
):
    """
    Get the schema for a source database
    
    Args:
        source_id: ID of the source database
        version: Specific version to fetch (default: current version)
        refresh: Whether to refresh the schema from the database (default: False)
    """
    # Get source database
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    # If refresh is requested, fetch new schema
    if refresh:
        response = fetch_and_store_schema(source_id, db)
        if response["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response["message"]
            )
        
    # Query for requested schema version
    schema_query = db.query(SchemaVersion).filter(SchemaVersion.source_db_id == source_id)
    
    if version:
        # Get specific version
        schema_version = schema_query.filter(SchemaVersion.version == version).first()
        if not schema_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema version {version} not found for source database ID {source_id}"
            )
        
    else:
        # Get current version
        schema_version = schema_query.filter(SchemaVersion.is_current == True).first()
        if not schema_version:
            # No schema versions yet, try fetching
            if not refresh:  # Only fetch if we haven't already tried
                return fetch_and_store_schema(source_id, db)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No schema available for source database ID {source_id}"
                )
            
    # Return schema with version info
    result = schema_version.schema
    result["_metadata"] = {
        "version": schema_version.version,
        "created_at": schema_version.created_at.isoformat(),
        "source_database": db_obj.name
    }
    
    return result

@router.get("/{source_id}/schema/versions", response_model=List[dict])
def get_schema_versions(
    source_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_session)
):
    """Get all schema versions for a source database"""
    # Check if source database exists
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    # Get all schema versions without the full schema JSON (for performance)
    schema_versions = db.query(
        SchemaVersion.id,
        SchemaVersion.version,
        SchemaVersion.is_current,
        SchemaVersion.created_at,
        SchemaVersion.hash
    ).filter(
        SchemaVersion.source_db_id == source_id
    ).order_by(desc(SchemaVersion.version)).limit(limit).all()
    
    result = []
    for sv in schema_versions:
        result.append({
            "id": sv.id,
            "version": sv.version,
            "is_current": sv.is_current,
            "created_at": sv.created_at.isoformat(),
            "hash": sv.hash
        })
    
    return result

@router.get("/{source_id}/schema/diff", response_model=dict)
def compare_schema_versions(
    source_id: int,
    version1: int,
    version2: int,
    db: Session = Depends(get_db_session)
):
    """
    Compare two schema versions and return differences
    
    Args:
        source_id: ID of the source database
        version1: First version to compare
        version2: Second version to compare
    """
    # Check if source database exists
    db_obj = db.query(SourceDatabase).filter(SourceDatabase.id == source_id).first()
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {source_id} not found"
        )
    
    # Get both schema versions
    schema1 = db.query(SchemaVersion).filter(
        SchemaVersion.source_db_id == source_id,
        SchemaVersion.version == version1
    ).first()
    
    schema2 = db.query(SchemaVersion).filter(
        SchemaVersion.source_db_id == source_id,
        SchemaVersion.version == version2
    ).first()

    if not schema1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema version {version1} not found for source database ID {source_id}"
        )
    
    if not schema2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema version {version2} not found for source database ID {source_id}"
        )
    
    # Calculate schema differences
    schema1_data = schema1.schema
    schema2_data = schema2.schema
    
    # Find added, removed, and modified tables
    tables1 = set(schema1_data.get("tables", {}).keys())
    tables2 = set(schema2_data.get("tables", {}).keys())
    
    added_tables = tables2 - tables1
    removed_tables = tables1 - tables2
    common_tables = tables1.intersection(tables2)

    # For common tables, check for column changes
    modified_tables = {}
    for table in common_tables:
        table1_cols = {c["name"]: c for c in schema1_data["tables"][table].get("columns", [])}
        table2_cols = {c["name"]: c for c in schema2_data["tables"][table].get("columns", [])}
        
        col_names1 = set(table1_cols.keys())
        col_names2 = set(table2_cols.keys())
        
        added_cols = col_names2 - col_names1
        removed_cols = col_names1 - col_names2
        common_cols = col_names1.intersection(col_names2)
        
        # Check for type changes in common columns
        changed_cols = {}
        for col in common_cols:
            if table1_cols[col]["data_type"] != table2_cols[col]["data_type"]:
                changed_cols[col] = {
                    "old_type": table1_cols[col]["data_type"],
                    "new_type": table2_cols[col]["data_type"]
                }
        
        # If there are any changes, add to modified tables
        if added_cols or removed_cols or changed_cols:
            modified_tables[table] = {
                "added_columns": list(added_cols),
                "removed_columns": list(removed_cols),
                "changed_columns": changed_cols
            }

    return {
        "metadata": {
            "version1": version1,
            "version2": version2,
            "created_at1": schema1.created_at.isoformat(),
            "created_at2": schema2.created_at.isoformat()
        },
        "changes": {
            "added_tables": list(added_tables),
            "removed_tables": list(removed_tables),
            "modified_tables": modified_tables
        }
    }