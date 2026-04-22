from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.v2 import CustomerV2, EventV2, RiskScoreV2


class RiskScoringServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def upsert_event_risk(
        self,
        event: EventV2,
        customer: CustomerV2,
        *,
        explanation: Dict[str, Any],
        score_type: str = "event_exposure",
    ) -> RiskScoreV2:
        exposure_matches: List[Dict[str, Any]] = explanation.get("exposure_matches", [])
        watchlist_matches: List[Dict[str, Any]] = explanation.get("matched_watchlists", [])
        document_count = int(explanation.get("document_count") or 0)
        evidence_factor = min(document_count / 5.0, 1.0)
        exposure_factor = max(
            [
                max(
                    float(match.get("criticality_score") or 0.0),
                    float(match.get("exposure_weight") or 0.0),
                )
                for match in exposure_matches
            ]
            or [0.0]
        )
        watchlist_factor = min(len(watchlist_matches) / 3.0, 1.0)
        event_confidence = float(event.confidence_score or 0.5)
        event_severity = float(event.severity_score or 0.5)

        score_value = (
            (0.45 * exposure_factor)
            + (0.15 * watchlist_factor)
            + (0.15 * evidence_factor)
            + (0.15 * event_confidence)
            + (0.10 * event_severity)
        )
        score_value = round(min(max(score_value, 0.0), 1.0), 4)
        severity = self._severity_from_score(score_value)
        confidence_score = round(min(max((event_confidence + evidence_factor) / 2.0, 0.0), 1.0), 4)

        rationale = self._build_rationale(
            exposure_matches=exposure_matches,
            watchlist_matches=watchlist_matches,
            document_count=document_count,
            score_value=score_value,
            severity=severity,
        )

        existing = (
            self.db.query(RiskScoreV2)
            .filter(
                RiskScoreV2.event_id == event.id,
                RiskScoreV2.customer_id == customer.id,
                RiskScoreV2.score_type == score_type,
            )
            .first()
        )
        metadata = {
            "exposure_match_count": len(exposure_matches),
            "watchlist_match_count": len(watchlist_matches),
            "document_count": document_count,
        }
        if existing:
            existing.score_value = score_value
            existing.confidence_score = confidence_score
            existing.severity = severity
            existing.rationale_text = rationale
            existing.scored_at = datetime.utcnow()
            existing.metadata_json = json.dumps(metadata)
            self.db.flush()
            return existing

        risk = RiskScoreV2(
            event_id=event.id,
            customer_id=customer.id,
            score_type=score_type,
            score_value=score_value,
            confidence_score=confidence_score,
            severity=severity,
            rationale_text=rationale,
            scored_at=datetime.utcnow(),
            metadata_json=json.dumps(metadata),
        )
        self.db.add(risk)
        self.db.flush()
        return risk

    def get_event_risk(self, event_id: str, customer_id: str, score_type: str = "event_exposure") -> Optional[RiskScoreV2]:
        return (
            self.db.query(RiskScoreV2)
            .filter(
                RiskScoreV2.event_id == event_id,
                RiskScoreV2.customer_id == customer_id,
                RiskScoreV2.score_type == score_type,
            )
            .first()
        )

    @staticmethod
    def _severity_from_score(score: float) -> str:
        if score >= 0.8:
            return "critical"
        if score >= 0.6:
            return "high"
        if score >= 0.35:
            return "medium"
        return "low"

    @staticmethod
    def _build_rationale(
        *,
        exposure_matches: List[Dict[str, Any]],
        watchlist_matches: List[Dict[str, Any]],
        document_count: int,
        score_value: float,
        severity: str,
    ) -> str:
        if exposure_matches:
            top = exposure_matches[0]
            object_name = top.get("source_object_name") or top.get("source_object_id")
            return (
                f"{severity.title()} risk ({score_value:.2f}) driven by exposure via "
                f"{top.get('source_object_type')} {object_name} and {document_count} supporting documents."
            )
        if watchlist_matches:
            return (
                f"{severity.title()} risk ({score_value:.2f}) driven by {len(watchlist_matches)} "
                f"watchlist matches and {document_count} supporting documents."
            )
        return f"{severity.title()} risk ({score_value:.2f}) with no mapped customer exposure yet."
