from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from croniter import croniter

from models.database import Connection, SourceDatabase, Destination, ScheduleType
from session_manager import get_db_session
from models.connection_api import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse
)
from models.api import StatusResponse

router = APIRouter(
    prefix="/connections",
    tags=["Connections"]
)

def calculate_next_run(cron_expression: str, timezone: str = "UTC") -> datetime:
    """Calculate the next run time based on a cron expression"""
    import pytz
    
    # Get the current time in the specified timezone
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    # Parse the cron expression and get the next occurrence
    cron = croniter(cron_expression, now)
    next_run = cron.get_next(datetime)
    
    return next_run

@router.post("/", response_model=ConnectionResponse)
def create_connection(
    data: ConnectionCreate, 
    db: Session = Depends(get_db_session)
):
    """Create new connection"""
    
    # Convert enum from API to database model
    schedule_type = ScheduleType.MANUAL
    if data.schedule_type == "cron":
        schedule_type = ScheduleType.CRON
    
    # Calculate next run time for cron schedules
    next_run_at = None
    if schedule_type == ScheduleType.CRON and data.cron_expression:
        try:
            next_run_at = calculate_next_run(
                data.cron_expression, 
                data.timezone
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cron expression: {str(e)}"
            )
    
    # Create connection settings
    conn_settings = Connection(
        name=data.name,
        schedule_type=schedule_type,
        cron_expression=data.cron_expression,
        timezone=data.timezone,
        is_active=data.is_active,
        connection_state=data.connection_state,
        next_run_at=next_run_at
    )
    
    db.add(conn_settings)
    db.commit()
    db.refresh(conn_settings)
    
    return conn_settings.to_dict()

@router.get("/", response_model=List[ConnectionResponse])
def list_connection(
    active_only: bool = False,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db_session)
):
    """List all connection"""
    query = db.query(Connection)
    
    if active_only:
        query = query.filter(Connection.is_active == True)
    
    settings = query.offset(skip).limit(limit).all()
    return [s.to_dict() for s in settings]

@router.get("/{id}", response_model=ConnectionResponse)
def get_connection(id: int, db: Session = Depends(get_db_session)):
    """Get specific connection"""
    settings = db.query(Connection).filter(Connection.id == id).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {id} not found"
        )
    
    return settings.to_dict()

@router.put("/{id}", response_model=ConnectionResponse)
def update_connection(
    id: int, 
    data: ConnectionUpdate, 
    db: Session = Depends(get_db_session)
):
    """Update connections"""
    settings = db.query(Connection).filter(Connection.id == id).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connections with ID {id} not found"
        )
    
    # Update only fields that were provided
    update_data = data.model_dump(exclude_unset=True)
    
    # Handle special case for schedule_type
    if "schedule_type" in update_data:
        schedule_type_value = update_data.pop("schedule_type")
        if schedule_type_value == "manual":
            settings.schedule_type = ScheduleType.MANUAL
        elif schedule_type_value == "cron":
            settings.schedule_type = ScheduleType.CRON
    
    # Apply other updates
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    # Recalculate next run time if cron settings changed
    if settings.schedule_type == ScheduleType.CRON and settings.cron_expression:
        try:
            settings.next_run_at = calculate_next_run(
                settings.cron_expression,
                settings.timezone
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cron expression: {str(e)}"
            )
    
    db.commit()
    db.refresh(settings)
    
    return settings.to_dict()

@router.delete("/{id}", response_model=StatusResponse)
def delete_connection(id: int, db: Session = Depends(get_db_session)):
    """Delete connection"""
    connection_data = db.query(Connection).filter(Connection.id == id).first()
    
    if not connection_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {id} not found"
        )
    
    db.delete(connection_data)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Connection '{connection_data.name}' deleted successfully"
    }

@router.post("/{id}/toggle", response_model=StatusResponse)
def toggle_connection_active(id: int, db: Session = Depends(get_db_session)):
    """Toggle connection active status"""
    connections = db.query(Connection).filter(Connection.id == id).first()
    
    if not connections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection settings with ID {id} not found"
        )
    
    connections.is_active = not connections.is_active
    db.commit()
    
    status_text = "activated" if connections.is_active else "deactivated"
    return {
        "status": "success",
        "message": f"Connection '{connections.name}' has been {status_text}"
    }