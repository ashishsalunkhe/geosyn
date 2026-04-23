from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.domain import Alert
from app.models.v2 import CustomerV2
from datetime import datetime, timedelta
from app.services.alert_service_v2 import AlertServiceV2
from app.workers.tasks import run_alert_generation

router = APIRouter()


class AlertActionRequest(BaseModel):
    action_type: str
    actor_id: str | None = None
    notes: str | None = None

@router.get("/", response_model=List[dict])
def read_alerts(
    db: Session = Depends(get_db),
    limit: int = 15
):
    """
    Retrieve recent proactive alerts.
    """
    alerts = db.query(Alert).filter(
        Alert.is_active == 1
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "type": a.type,
            "severity": a.severity,
            "ticker": a.ticker,
            "title": a.title,
            "content": a.content,
            "context_snippet": a.context_snippet,
            "created_at": a.created_at.isoformat(),
            "alert_payload": a.alert_payload
        } for a in alerts
    ]

@router.post("/clear")
def clear_alerts(db: Session = Depends(get_db)):
    """
    Deactivate all current alerts.
    """
    db.query(Alert).update({Alert.is_active: 0})
    db.commit()
    return {"status": "ok"}


@router.get("/v2", response_model=List[dict])
def read_alerts_v2(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
    limit: int = 25,
    status: str | None = None,
):
    service = AlertServiceV2(db)
    alerts = service.list_alerts(current_customer.id, limit=limit, status=status)
    return [
        {
            "id": a.id,
            "event_id": a.event_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "status": a.status,
            "headline": a.headline,
            "summary_text": a.summary_text,
            "recommended_action": a.recommended_action,
            "triggered_at": a.triggered_at.isoformat(),
            "metadata": service.parse_metadata(a),
        }
        for a in alerts
    ]


@router.post("/v2/generate", response_model=dict)
def generate_alerts_v2(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
    enqueue: bool = False,
):
    if enqueue:
        task = run_alert_generation.delay(current_customer.id)
        return {"status": "queued", "task_id": task.id, "task_name": "run_alert_generation"}
    service = AlertServiceV2(db)
    return {"status": "success", **service.generate_for_customer(current_customer)}


@router.get("/v2/{alert_id}", response_model=dict)
def read_alert_v2(
    alert_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = AlertServiceV2(db)
    alert = service.get_alert(alert_id, current_customer.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {
        "id": alert.id,
        "event_id": alert.event_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "status": alert.status,
        "headline": alert.headline,
        "summary_text": alert.summary_text,
        "recommended_action": alert.recommended_action,
        "triggered_at": alert.triggered_at.isoformat(),
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "metadata": service.parse_metadata(alert),
    }


@router.get("/v2/{alert_id}/evidence", response_model=List[dict])
def read_alert_v2_evidence(
    alert_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = AlertServiceV2(db)
    return service.list_evidence(alert_id, current_customer.id)


@router.post("/v2/{alert_id}/actions", response_model=dict)
def add_alert_v2_action(
    alert_id: str,
    payload: AlertActionRequest,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = AlertServiceV2(db)
    try:
        return service.add_action(alert_id, current_customer.id, payload.action_type, payload.actor_id, payload.notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/v2/{alert_id}/actions", response_model=List[dict])
def read_alert_v2_actions(
    alert_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = AlertServiceV2(db)
    return service.list_actions(alert_id, current_customer.id)


@router.get("/v2/workflow/config", response_model=dict)
def read_alert_v2_workflow_config(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = AlertServiceV2(db)
    return service.workflow_config()
