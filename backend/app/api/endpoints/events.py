from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import domain as schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.EventCluster])
def read_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    from app.models.domain import EventCluster
    return db.query(EventCluster).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=schemas.EventCluster)
def read_event_by_id(
    id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get event by ID.
    """
    from app.models.domain import EventCluster
    cluster = db.query(EventCluster).filter(EventCluster.id == id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Event cluster not found")
    return cluster
