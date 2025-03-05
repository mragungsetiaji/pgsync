from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from croniter import croniter

from models.database import ConnectionSettings, ScheduleType
from session_manager import get_db_session
from models.api import (
    ConnectionSettingsCreate,
    ConnectionSettingsUpdate,
    ConnectionSettingsResponse,
    StatusResponse
)

router = APIRouter(
    prefix="/connection-settings",
    tags=["Connection Settings"]
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

@router.post("/", response_model=ConnectionSettingsResponse)
def create_connection_settings(
    settings_data: ConnectionSettingsCreate, 
    db: Session = Depends(get_db_session)
):
    """Create new connection settings"""
    
    # Convert enum from API to database model
    schedule_type = ScheduleType.MANUAL
    if settings_data.schedule_type == "cron":
        schedule_type = ScheduleType.CRON
    
    # Calculate next run time for cron schedules
    next_run_at = None
    if schedule_type == ScheduleType.CRON and settings_data.cron_expression:
        try:
            next_run_at = calculate_next_run(
                settings_data.cron_expression, 
                settings_data.timezone
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cron expression: {str(e)}"
            )
    
    # Create connection settings
    conn_settings = ConnectionSettings(
        name=settings_data.name,
        schedule_type=schedule_type,
        cron_expression=settings_data.cron_expression,
        timezone=settings_data.timezone,
        is_active=settings_data.is_active,
        connection_state=settings_data.connection_state,
        next_run_at=next_run_at
    )
    
    db.add(conn_settings)
    db.commit()
    db.refresh(conn_settings)
    
    return conn_settings.to_dict()

@router.get("/", response_model=List[ConnectionSettingsResponse])
def list_connection_settings(
    active_only: bool = False,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db_session)
):
    """List all connection settings"""
    query = db.query(ConnectionSettings)
    
    if active_only:
        query = query.filter(ConnectionSettings.is_active == True)
    
    settings = query.offset(skip).limit(limit).all()
    return [s.to_dict() for s in settings]

@router.get("/{settings_id}", response_model=ConnectionSettingsResponse)
def get_connection_settings(settings_id: int, db: Session = Depends(get_db_session)):
    """Get specific connection settings"""
    settings = db.query(ConnectionSettings).filter(ConnectionSettings.id == settings_id).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection settings with ID {settings_id} not found"
        )
    
    return settings.to_dict()

@router.put("/{settings_id}", response_model=ConnectionSettingsResponse)
def update_connection_settings(
    settings_id: int, 
    settings_data: ConnectionSettingsUpdate, 
    db: Session = Depends(get_db_session)
):
    """Update connection settings"""
    settings = db.query(ConnectionSettings).filter(ConnectionSettings.id == settings_id).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection settings with ID {settings_id} not found"
        )
    
    # Update only fields that were provided
    update_data = settings_data.dict(exclude_unset=True)
    
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

@router.delete("/{settings_id}", response_model=StatusResponse)
def delete_connection_settings(settings_id: int, db: Session = Depends(get_db_session)):
    """Delete connection settings"""
    settings = db.query(ConnectionSettings).filter(ConnectionSettings.id == settings_id).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection settings with ID {settings_id} not found"
        )
    
    db.delete(settings)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Connection settings '{settings.name}' deleted successfully"
    }

@router.post("/{settings_id}/toggle", response_model=StatusResponse)
def toggle_connection_active(settings_id: int, db: Session = Depends(get_db_session)):
    """Toggle connection settings active status"""
    settings = db.query(ConnectionSettings).filter(ConnectionSettings.id == settings_id).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection settings with ID {settings_id} not found"
        )
    
    settings.is_active = not settings.is_active
    db.commit()
    
    status_text = "activated" if settings.is_active else "deactivated"
    return {
        "status": "success",
        "message": f"Connection '{settings.name}' has been {status_text}"
    }