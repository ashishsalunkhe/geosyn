from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.domain import Alert
from datetime import datetime, timedelta

router = APIRouter()

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
