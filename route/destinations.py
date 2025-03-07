from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.database import Destination, Connection
from session_manager import get_db_session
from models.destination_api import (
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
    TestBigQueryConnectionRequest
)
from models.api import StatusResponse
from services.bigquery import BigQueryDestination

router = APIRouter(
    prefix="/destinations",
    tags=["Destinations"]
)

@router.post("/", response_model=DestinationResponse)
def create_destination(
    destination_data: DestinationCreate, 
    db: Session = Depends(get_db_session)
):
    """Create a new destination"""
    
    # Test the connection first
    try:
        bq = BigQueryDestination(
            project_id=destination_data.project_id,
            dataset=destination_data.dataset,
            credentials=destination_data.credentials,
            bucket_name=destination_data.bucket_name,
            folder_path=destination_data.folder_path,
            hmac_key=destination_data.hmac_key,
            hmac_secret=destination_data.hmac_secret
        )
        
        if not bq.check_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not connect to BigQuery or GCS with the provided credentials"
            )
            
        # Check if dataset exists
        if not bq.check_dataset_exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset '{destination_data.dataset}' does not exist in project '{destination_data.project_id}'"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create the destination entry
    destination = Destination(
        name=destination_data.name,
        type="bigquery",
        project_id=destination_data.project_id,
        dataset=destination_data.dataset,
        credentials=destination_data.credentials,
        bucket_name=destination_data.bucket_name,
        folder_path=destination_data.folder_path,
        hmac_key=destination_data.hmac_key,
        hmac_secret=destination_data.hmac_secret,
        is_active=destination_data.is_active
    )
    
    db.add(destination)
    db.commit()
    db.refresh(destination)
    
    return destination.to_dict()

@router.get("/", response_model=List[DestinationResponse])
def get_destinations(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False,
    db: Session = Depends(get_db_session)
):
    """Get all destinations"""
    query = db.query(Destination)
    
    if active_only:
        query = query.filter(Destination.is_active == True)
    
    destinations = query.offset(skip).limit(limit).all()
    return [destination.to_dict() for destination in destinations]

@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination(destination_id: int, db: Session = Depends(get_db_session)):
    """Get a specific destination"""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )
    
    return destination.to_dict()

@router.put("/{destination_id}", response_model=DestinationResponse)
def update_destination(
    destination_id: int, 
    destination_data: DestinationUpdate, 
    db: Session = Depends(get_db_session)
):
    """Update a destination"""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )
    
    # Update attributes that were provided
    update_data = destination_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(destination, key, value)
    
    db.commit()
    db.refresh(destination)
    
    return destination.to_dict()

@router.delete("/{destination_id}", response_model=StatusResponse)
def delete_destination(destination_id: int, db: Session = Depends(get_db_session)):
    """Delete a destination"""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )
    
    # Check if destination is in use by any connections
    connection_count = db.query(Connection).filter(Connection.destination_id == destination_id).count()
    if connection_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete destination as it is used by {connection_count} connection(s)"
        )
    
    db.delete(destination)
    db.commit()
    
    return {"status": "success", "message": f"Destination '{destination.name}' deleted successfully"}

@router.post("/test-connection", response_model=StatusResponse)
def test_connection(conn_data: TestBigQueryConnectionRequest):
    """Test a BigQuery connection without saving it"""
    try:
        bq = BigQueryDestination(
            project_id=conn_data.project_id,
            dataset=conn_data.dataset,
            credentials=conn_data.credentials,
            bucket_name=conn_data.bucket_name,
            folder_path=conn_data.folder_path,
            hmac_key=conn_data.hmac_key,
            hmac_secret=conn_data.hmac_secret
        )
        
        if not bq.check_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not connect to BigQuery or GCS with the provided credentials"
            )
            
        # Check if dataset exists
        dataset_exists = bq.check_dataset_exists()
        
        return {
            "status": "success", 
            "message": "Connection successful" + (", dataset exists" if dataset_exists else ", but dataset does not exist")
        }
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )