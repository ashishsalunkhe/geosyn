from typing import List, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.schemas import domain as schemas
from app.services.evaluation_service_v2 import EvaluationServiceV2
from app.services.event_service_v2 import EventServiceV2
from app.services.event_timeline_service_v2 import EventTimelineServiceV2

router = APIRouter()


class EvaluationLabelRequest(BaseModel):
    label_type: str
    label_value: str
    notes: str | None = None
    labeled_by: str | None = None

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


@router.get("/v2/{event_id}/timeline", response_model=List[schemas.EventTimelineV2])
def read_event_v2_timeline(
    event_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    event_service = EventServiceV2(db)
    event = event_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Canonical event not found")
    timeline_service = EventTimelineServiceV2(db)
    rows = timeline_service.ensure_timelines_for_event(event)
    return [timeline_service.serialize_timeline(row) for row in rows]


@router.get("/v2/{event_id}/risk", response_model=dict)
def read_event_v2_risk(
    event_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    service = EventServiceV2(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Canonical event not found")
    explanation = service.explain_event_for_customer(event_id, current_customer.id)
    return explanation.get("risk_score") or {"detail": "No risk score available"}


@router.get("/v2/{event_id}/evaluation", response_model=List[schemas.EvalLabelV2])
def read_event_v2_evaluation_labels(
    event_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    service = EventServiceV2(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Canonical event not found")
    evaluation_service = EvaluationServiceV2(db)
    labels = evaluation_service.list_labels(event_id, current_customer.id)
    return [
        {
            "id": row.id,
            "label_type": row.label_type,
            "label_value": row.label_value,
            "notes": row.notes,
            "labeled_by": row.labeled_by,
            "labeled_at": row.labeled_at,
            "alert_id": row.alert_id,
            "customer_id": row.customer_id,
            "metadata": service._parse_json(row.metadata_json),
        }
        for row in labels
    ]


@router.post("/v2/{event_id}/evaluation", response_model=schemas.EvalLabelV2)
def add_event_v2_evaluation_label(
    event_id: str,
    payload: EvaluationLabelRequest,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    service = EventServiceV2(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Canonical event not found")
    evaluation_service = EvaluationServiceV2(db)
    label = evaluation_service.add_label(
        event_id=event_id,
        customer_id=current_customer.id,
        alert_id=None,
        label_type=payload.label_type,
        label_value=payload.label_value,
        notes=payload.notes,
        labeled_by=payload.labeled_by,
    )
    return {
        "id": label.id,
        "label_type": label.label_type,
        "label_value": label.label_value,
        "notes": label.notes,
        "labeled_by": label.labeled_by,
        "labeled_at": label.labeled_at,
        "alert_id": label.alert_id,
        "customer_id": label.customer_id,
        "metadata": service._parse_json(label.metadata_json),
    }

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
