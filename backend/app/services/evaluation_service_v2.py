from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.v2 import EvalLabelV2


class EvaluationServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def list_labels(self, event_id: str, customer_id: Optional[str] = None) -> List[EvalLabelV2]:
        query = self.db.query(EvalLabelV2).filter(EvalLabelV2.event_id == event_id)
        if customer_id:
            query = query.filter((EvalLabelV2.customer_id == customer_id) | (EvalLabelV2.customer_id.is_(None)))
        return query.order_by(EvalLabelV2.labeled_at.desc()).all()

    def add_label(
        self,
        *,
        event_id: str,
        customer_id: Optional[str],
        alert_id: Optional[str],
        label_type: str,
        label_value: str,
        notes: Optional[str],
        labeled_by: Optional[str],
        metadata: Optional[Dict[str, object]] = None,
    ) -> EvalLabelV2:
        label = EvalLabelV2(
            event_id=event_id,
            customer_id=customer_id,
            alert_id=alert_id,
            label_type=label_type,
            label_value=label_value,
            notes=notes,
            labeled_by=labeled_by,
            labeled_at=datetime.utcnow(),
            metadata_json=json.dumps(metadata or {}),
        )
        self.db.add(label)
        self.db.commit()
        self.db.refresh(label)
        return label
