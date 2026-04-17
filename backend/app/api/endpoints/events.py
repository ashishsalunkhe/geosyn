from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.schemas import domain as schemas
from app.services.event_service_v2 import EventServiceV2

router = APIRouter()

@router.get("/", response_model=List[schemas.EventCluster])
def read_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    from app.models.domain import EventCluster
    return db.query(EventCluster).offset(skip).limit(limit).all()


@router.get("/v2", response_model=List[schemas.EventV2Summary])
def read_events_v2(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
) -> Any:
    service = EventServiceV2(db)
    events = service.list_events(skip=skip, limit=limit)
    if event_type:
        events = [event for event in events if event.event_type == event_type]
    if status:
        events = [event for event in events if event.status == status]
    return [service.serialize_event(event, customer_id=current_customer.id) for event in events]


@router.get("/v2/{event_id}", response_model=schemas.EventV2Detail)
def read_event_v2_by_id(
    event_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    service = EventServiceV2(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Canonical event not found")
    return service.serialize_event(event, customer_id=current_customer.id)


@router.get("/v2/{event_id}/exposure", response_model=dict)
def read_event_v2_exposure(
    event_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    service = EventServiceV2(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Canonical event not found")
    return service.explain_event_for_customer(event_id, current_customer.id)

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
