from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from models.database import SyncTable, Source, SchemaVersion
from session_manager import get_db_session
from models.api import StatusResponse, SyncTableCreate, SyncTableResponse, SyncTableUpdate
from connector.postgres_source import PostgresSource

router = APIRouter(
    prefix="/sync-tables",
    tags=["Sync Tables"]
)


@router.post("/", response_model=SyncTableResponse)
def create_sync_table(table_data: SyncTableCreate, db: Session = Depends(get_db_session)):
    """Add a table to be synced"""
    # Check if source database exists
    source_db = db.query(Source).filter(Source.id == table_data.source_db_id).first()
    if not source_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source database with ID {table_data.source_db_id} not found"
        )
    
    # Get the current schema version for this source
    schema_version = db.query(SchemaVersion).filter(
        SchemaVersion.source_db_id == table_data.source_db_id,
        SchemaVersion.is_current == True
    ).first()

    if schema_version:
        # Validate that the table exists in the schema
        schema_data = schema_version.schema
        tables = schema_data.get("tables", {})
        
        if table_data.table_name not in tables:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table '{table_data.table_name}' not found in the current schema (version {schema_version.version})"
            )
            
        # Validate that the cursor column exists in the table
        table_schema = tables[table_data.table_name]
        columns = table_schema.get("columns", [])
        column_names = [col.get("name") for col in columns]
        
        if table_data.cursor_column not in column_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{table_data.cursor_column}' not found in table '{table_data.table_name}'"
            )
    else:
        # No schema stored yet, we'll skip validation but log a warning
        import logging
        logging.warning(
            f"No schema version found for source_db_id={table_data.source_db_id}. "
            f"Skipping table and column validation."
        )
    
    # Create sync table entry
    sync_table = SyncTable(
        source_db_id=table_data.source_db_id,
        table_name=table_data.table_name,
        is_active=table_data.is_active,
        cursor_column=table_data.cursor_column,
        batch_size=table_data.batch_size,
        sync_interval=table_data.sync_interval
    )
    
    try:
        db.add(sync_table)
        db.commit()
        db.refresh(sync_table)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Table '{table_data.table_name}' is already configured for syncing"
        )
    
    # Return with source_db_name included
    response = sync_table.to_dict()
    response["source_db_name"] = source_db.name
    return response

@router.get("/", response_model=List[SyncTableResponse])
def list_sync_tables(
    source_db_id: Optional[int] = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """List all tables configured for syncing"""
    query = db.query(SyncTable, Source.name.label("source_db_name")) \
              .join(Source)
    
    # Filter by source database if provided
    if source_db_id is not None:
        query = query.filter(SyncTable.source_db_id == source_db_id)
    
    # Filter by active status if requested
    if active_only:
        query = query.filter(SyncTable.is_active == True)
    
    # Apply pagination
    result = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    response = []
    for sync_table, source_db_name in result:
        item = sync_table.to_dict()
        item["source_db_name"] = source_db_name
        response.append(item)
    
    return response

@router.get("/{sync_table_id}", response_model=SyncTableResponse)
def get_sync_table(sync_table_id: int, db: Session = Depends(get_db_session)):
    """Get a specific sync table configuration"""
    result = db.query(SyncTable, Source.name.label("source_db_name")) \
               .join(Source) \
               .filter(SyncTable.id == sync_table_id) \
               .first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync table with ID {sync_table_id} not found"
        )
    
    sync_table, source_db_name = result
    response = sync_table.to_dict()
    response["source_db_name"] = source_db_name
    
    return response

@router.put("/{sync_table_id}", response_model=SyncTableResponse)
def update_sync_table(sync_table_id: int, table_data: SyncTableUpdate, db: Session = Depends(get_db_session)):
    """Update a sync table configuration"""
    result = db.query(SyncTable, Source) \
               .join(Source) \
               .filter(SyncTable.id == sync_table_id) \
               .first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync table with ID {sync_table_id} not found"
        )
    
    sync_table, source_db = result
    
    # If updating cursor column, validate it exists in the table
    if table_data.cursor_column is not None:
        source = PostgresSource(
            host=source_db.host,
            port=source_db.port,
            database=source_db.database,
            user=source_db.user,
            password=source_db.password
        )
        
        columns = source.fetch_columns(sync_table.table_name)
        column_names = [col["name"] for col in columns]
        
        if table_data.cursor_column not in column_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{table_data.cursor_column}' not found in table '{sync_table.table_name}'"
            )
    
        # Update fields that were provided
        update_data = table_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sync_table, key, value)
        
        # Save changes
        db.commit()
        db.refresh(sync_table)
        
        # Return with source_db_name included
        response = sync_table.to_dict()
        response["source_db_name"] = source_db.name
        
        return response

@router.delete("/{sync_table_id}", response_model=StatusResponse)
def delete_sync_table(sync_table_id: int, db: Session = Depends(get_db_session)):
    """Remove a table from syncing"""
    sync_table = db.query(SyncTable).filter(SyncTable.id == sync_table_id).first()
    
    if not sync_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync table with ID {sync_table_id} not found"
        )
    
    # Delete the sync table configuration
    db.delete(sync_table)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Sync configuration for table '{sync_table.table_name}' removed"
    }

@router.post("/{sync_table_id}/toggle", response_model=StatusResponse)
def toggle_sync_table(sync_table_id: int, db: Session = Depends(get_db_session)):
    """Toggle whether a table is actively synced"""
    sync_table = db.query(SyncTable).filter(SyncTable.id == sync_table_id).first()
    
    if not sync_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync table with ID {sync_table_id} not found"
        )
    
    # Toggle the active status
    sync_table.is_active = not sync_table.is_active
    db.commit()
    
    status_msg = "activated" if sync_table.is_active else "deactivated"
    return {
        "status": "success",
        "message": f"Sync for '{sync_table.table_name}' has been {status_msg}"
    }