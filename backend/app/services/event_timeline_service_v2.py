from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.v2 import EventEvidenceV2, EventTimelineV2, EventV2, EvidenceDocumentV2


class EventTimelineServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def list_timelines(self, event_id: str) -> List[EventTimelineV2]:
        return (
            self.db.query(EventTimelineV2)
            .filter(EventTimelineV2.event_id == event_id)
            .order_by(EventTimelineV2.occurred_at.asc(), EventTimelineV2.id.asc())
            .all()
        )

    def ensure_timelines_for_event(self, event: EventV2) -> List[EventTimelineV2]:
        evidence_rows = (
            self.db.query(EventEvidenceV2)
            .filter(EventEvidenceV2.event_id == event.id)
            .order_by(EventEvidenceV2.created_at.asc())
            .all()
        )
        created: List[EventTimelineV2] = []
        for row in evidence_rows:
            evidence_doc = (
                self.db.query(EvidenceDocumentV2)
                .filter(EvidenceDocumentV2.legacy_document_id == row.legacy_document_id)
                .first()
            )
            if not evidence_doc:
                continue
            occurred_at = evidence_doc.event_time or evidence_doc.published_at or event.first_seen_at or datetime.utcnow()
            existing = (
                self.db.query(EventTimelineV2)
                .filter(
                    EventTimelineV2.event_id == event.id,
                    EventTimelineV2.source_document_id == evidence_doc.id,
                    EventTimelineV2.timeline_type == "evidence",
                )
                .first()
            )
            if existing:
                created.append(existing)
                continue

            timeline = EventTimelineV2(
                event_id=event.id,
                occurred_at=occurred_at,
                title=evidence_doc.title or event.canonical_title,
                description=evidence_doc.summary_text or self._trim(evidence_doc.body_text),
                source_document_id=evidence_doc.id,
                timeline_type="evidence",
                metadata_json=json.dumps(
                    {
                        "is_primary": row.is_primary,
                        "contribution_type": row.contribution_type,
                        "relevance_score": row.relevance_score,
                    }
                ),
                created_at=datetime.utcnow(),
            )
            self.db.add(timeline)
            self.db.flush()
            created.append(timeline)
        return created

    def serialize_timeline(self, row: EventTimelineV2) -> Dict[str, Any]:
        return {
            "id": row.id,
            "event_id": row.event_id,
            "occurred_at": row.occurred_at.isoformat() if row.occurred_at else None,
            "title": row.title,
            "description": row.description,
            "source_document_id": row.source_document_id,
            "timeline_type": row.timeline_type,
            "metadata": self._parse_json(row.metadata_json),
        }

    @staticmethod
    def _trim(text: str | None, limit: int = 280) -> str | None:
        if not text:
            return None
        normalized = " ".join(text.split())
        return normalized[:limit] if normalized else None

    @staticmethod
    def _parse_json(payload: str | None) -> Any:
        if not payload:
            return None
        try:
            return json.loads(payload)
        except Exception:  # noqa: BLE001
            return payload
