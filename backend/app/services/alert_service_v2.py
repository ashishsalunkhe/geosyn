import json
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.v2 import AlertActionV2, AlertEvidenceV2, AlertV2, CustomerV2, EventEvidenceV2
from app.services.event_service_v2 import EventServiceV2
from app.core.metrics import alerts_generated_total


class AlertServiceV2:
    STATUS_TRANSITIONS = {
        "new": {"review", "monitor", "escalated", "dismissed", "mitigated"},
        "review": {"monitor", "escalated", "dismissed", "mitigated"},
        "monitor": {"review", "escalated", "dismissed", "mitigated"},
        "escalated": {"monitor", "dismissed", "mitigated"},
        "dismissed": set(),
        "mitigated": set(),
    }

    def __init__(self, db: Session):
        self.db = db
        self.event_service = EventServiceV2(db)

    def generate_for_customer(self, customer: CustomerV2, limit: int = 100) -> Dict[str, object]:
        events = self.event_service.list_events(limit=limit, skip=0)
        created = 0
        reused = 0

        for event in events:
            explanation = self.event_service.explain_event_for_customer(event.id, customer.id)
            if not explanation["exposure_matches"]:
                continue

            existing = (
                self.db.query(AlertV2)
                .filter(AlertV2.customer_id == customer.id, AlertV2.event_id == event.id)
                .first()
            )
            if existing:
                reused += 1
                continue

            top_match = explanation["exposure_matches"][0]
            severity = explanation.get("risk_score", {}).get("severity") or self._derive_severity(top_match)
            alert = AlertV2(
                customer_id=customer.id,
                event_id=event.id,
                alert_type="event_exposure",
                severity=severity,
                status="new",
                headline=event.canonical_title,
                summary_text=explanation["summary"],
                recommended_action=self._recommended_action(severity),
                triggered_at=datetime.utcnow(),
                metadata_json=json.dumps(
                    {
                        "risk_score": explanation.get("risk_score"),
                        "top_exposure_match": top_match,
                    }
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(alert)
            self.db.flush()

            evidence_rows = (
                self.db.query(EventEvidenceV2)
                .filter(EventEvidenceV2.event_id == event.id)
                .order_by(EventEvidenceV2.is_primary.desc(), EventEvidenceV2.created_at.asc())
                .limit(3)
                .all()
            )
            for evidence in evidence_rows:
                self.db.add(
                    AlertEvidenceV2(
                        alert_id=alert.id,
                        legacy_document_id=evidence.legacy_document_id,
                        evidence_type="event_support",
                        relevance_score=evidence.relevance_score,
                        created_at=datetime.utcnow(),
                    )
                )
            created += 1

        self.db.commit()
        alerts_generated_total.labels(customer.slug).inc(created)
        return {"created": created, "reused": reused}

    def list_alerts(self, customer_id: str, limit: int = 50, status: Optional[str] = None) -> List[AlertV2]:
        query = self.db.query(AlertV2).filter(AlertV2.customer_id == customer_id)
        if status:
            query = query.filter(AlertV2.status == status)
        return (
            query
            .order_by(AlertV2.triggered_at.desc())
            .limit(limit)
            .all()
        )

    def get_alert(self, alert_id: str, customer_id: str) -> Optional[AlertV2]:
        return (
            self.db.query(AlertV2)
            .filter(AlertV2.id == alert_id, AlertV2.customer_id == customer_id)
            .first()
        )

    def list_evidence(self, alert_id: str, customer_id: str) -> List[Dict[str, object]]:
        alert = self.get_alert(alert_id, customer_id)
        if not alert:
            return []

        rows = (
            self.db.query(AlertEvidenceV2)
            .filter(AlertEvidenceV2.alert_id == alert.id)
            .order_by(AlertEvidenceV2.created_at.asc())
            .all()
        )
        result = []
        for row in rows:
            doc = row.legacy_document
            result.append(
                {
                    "document_id": doc.id,
                    "title": doc.title,
                    "url": doc.url,
                    "published_at": doc.published_at.isoformat() if doc.published_at else None,
                    "evidence_type": row.evidence_type,
                    "relevance_score": row.relevance_score,
                }
            )
        return result

    def list_actions(self, alert_id: str, customer_id: str) -> List[Dict[str, object]]:
        alert = self.get_alert(alert_id, customer_id)
        if not alert:
            return []
        rows = (
            self.db.query(AlertActionV2)
            .filter(AlertActionV2.alert_id == alert.id)
            .order_by(AlertActionV2.created_at.asc())
            .all()
        )
        return [
            {
                "id": row.id,
                "action_type": row.action_type,
                "actor_id": row.actor_id,
                "notes": row.notes,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]

    def add_action(self, alert_id: str, customer_id: str, action_type: str, actor_id: Optional[str], notes: Optional[str]) -> Dict[str, str]:
        alert = self.get_alert(alert_id, customer_id)
        if not alert:
            raise ValueError("Alert not found")

        normalized_action = action_type.strip().lower()
        if normalized_action not in {"review", "monitor", "escalated", "dismissed", "mitigated"}:
            raise ValueError(f"Unsupported alert action '{action_type}'")

        current_status = (alert.status or "new").lower()
        allowed = self.STATUS_TRANSITIONS.get(current_status, set())
        if normalized_action not in allowed:
            raise ValueError(
                f"Action '{normalized_action}' is not allowed when alert status is '{current_status}'"
            )

        action = AlertActionV2(
            alert_id=alert.id,
            action_type=normalized_action,
            actor_id=actor_id,
            notes=notes,
            created_at=datetime.utcnow(),
        )
        self.db.add(action)
        alert.status = normalized_action
        alert.updated_at = datetime.utcnow()
        if normalized_action in {"dismissed", "mitigated"}:
            alert.resolved_at = datetime.utcnow()
        else:
            alert.resolved_at = None
        self.db.commit()
        return {"status": "ok", "action_type": normalized_action, "alert_status": alert.status}

    def workflow_config(self) -> Dict[str, object]:
        return {
            "initial_status": "new",
            "terminal_statuses": ["dismissed", "mitigated"],
            "allowed_actions": ["review", "monitor", "escalated", "dismissed", "mitigated"],
            "transitions": {status: sorted(actions) for status, actions in self.STATUS_TRANSITIONS.items()},
        }

    @staticmethod
    def _derive_severity(match: Dict[str, object]) -> str:
        criticality = float(match.get("criticality_score") or 0)
        exposure_weight = float(match.get("exposure_weight") or 0)
        score = max(criticality, exposure_weight)
        if score >= 0.85:
            return "critical"
        if score >= 0.6:
            return "high"
        if score >= 0.3:
            return "medium"
        return "low"

    @staticmethod
    def _recommended_action(severity: str) -> str:
        mapping = {
            "critical": "Escalate immediately to continuity and sourcing stakeholders.",
            "high": "Review exposure and assign an owner within the current shift.",
            "medium": "Monitor and assess exposure relevance within 24 hours.",
            "low": "Track only unless additional signals accumulate.",
        }
        return mapping[severity]

    @staticmethod
    def parse_metadata(alert: AlertV2) -> object:
        if not alert.metadata_json:
            return None
        try:
            return json.loads(alert.metadata_json)
        except Exception:  # noqa: BLE001
            return alert.metadata_json
