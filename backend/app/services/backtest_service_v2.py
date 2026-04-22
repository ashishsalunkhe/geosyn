from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.v2 import AlertV2, BacktestRunV2, CustomerV2, EvalLabelV2, RiskScoreV2


class BacktestServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def compute_metrics(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        alerts_query = self.db.query(AlertV2)
        risk_query = self.db.query(RiskScoreV2)
        labels_query = self.db.query(EvalLabelV2)
        if customer_id:
            alerts_query = alerts_query.filter(AlertV2.customer_id == customer_id)
            risk_query = risk_query.filter(RiskScoreV2.customer_id == customer_id)
            labels_query = labels_query.filter(
                (EvalLabelV2.customer_id == customer_id) | (EvalLabelV2.customer_id.is_(None))
            )

        alerts = alerts_query.all()
        risk_scores = risk_query.all()
        labels = labels_query.all()

        label_groups: Dict[str, List[EvalLabelV2]] = {}
        for label in labels:
            label_groups.setdefault(label.label_type, []).append(label)

        useful_labels = label_groups.get("alert_was_useful", [])
        material_labels = label_groups.get("event_was_material", [])
        false_positive_labels = label_groups.get("false_positive", [])
        lead_time_labels = label_groups.get("lead_time_hours", [])
        disruption_labels = label_groups.get("disruption_occurred", [])

        useful_true = self._count_label_value(useful_labels, {"true", "yes", "useful", "1"})
        material_true = self._count_label_value(material_labels, {"true", "yes", "material", "1"})
        false_positive_true = self._count_label_value(false_positive_labels, {"true", "yes", "1"})
        disruption_true = self._count_label_value(disruption_labels, {"true", "yes", "1"})
        lead_time_values = self._parse_numeric_labels(lead_time_labels)

        metrics = {
            "customer_id": customer_id,
            "alert_count": len(alerts),
            "risk_score_count": len(risk_scores),
            "label_count": len(labels),
            "average_risk_score": round(sum(score.score_value for score in risk_scores) / len(risk_scores), 4)
            if risk_scores
            else None,
            "severity_distribution": self._severity_distribution(risk_scores),
            "useful_alert_rate": round(useful_true / len(useful_labels), 4) if useful_labels else None,
            "material_event_rate": round(material_true / len(material_labels), 4) if material_labels else None,
            "false_positive_rate": round(false_positive_true / len(false_positive_labels), 4)
            if false_positive_labels
            else None,
            "disruption_rate": round(disruption_true / len(disruption_labels), 4) if disruption_labels else None,
            "average_lead_time_hours": round(sum(lead_time_values) / len(lead_time_values), 2)
            if lead_time_values
            else None,
            "high_or_critical_alert_share": round(
                len([alert for alert in alerts if alert.severity in {"high", "critical"}]) / len(alerts), 4
            )
            if alerts
            else None,
        }
        return metrics

    def list_runs(self, customer_id: Optional[str] = None, limit: int = 25) -> List[BacktestRunV2]:
        query = self.db.query(BacktestRunV2)
        if customer_id:
            query = query.filter((BacktestRunV2.customer_id == customer_id) | (BacktestRunV2.customer_id.is_(None)))
        return query.order_by(BacktestRunV2.started_at.desc()).limit(limit).all()

    def create_run(
        self,
        *,
        run_name: str,
        customer: Optional[CustomerV2],
        config: Optional[Dict[str, Any]] = None,
    ) -> BacktestRunV2:
        started_at = datetime.utcnow()
        metrics = self.compute_metrics(customer.id if customer else None)
        run = BacktestRunV2(
            run_name=run_name,
            customer_id=customer.id if customer else None,
            config_json=json.dumps(config or {}),
            metrics_json=json.dumps(metrics),
            started_at=started_at,
            completed_at=datetime.utcnow(),
            status="completed",
            created_at=started_at,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    @staticmethod
    def serialize_run(run: BacktestRunV2) -> Dict[str, Any]:
        return {
            "id": run.id,
            "run_name": run.run_name,
            "customer_id": run.customer_id,
            "config": BacktestServiceV2._parse_json(run.config_json),
            "metrics": BacktestServiceV2._parse_json(run.metrics_json),
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "status": run.status,
        }

    @staticmethod
    def _severity_distribution(scores: List[RiskScoreV2]) -> Dict[str, int]:
        distribution: Dict[str, int] = {}
        for score in scores:
            distribution[score.severity] = distribution.get(score.severity, 0) + 1
        return distribution

    @staticmethod
    def _count_label_value(labels: List[EvalLabelV2], accepted_values: set[str]) -> int:
        return sum(1 for label in labels if (label.label_value or "").strip().lower() in accepted_values)

    @staticmethod
    def _parse_numeric_labels(labels: List[EvalLabelV2]) -> List[float]:
        values: List[float] = []
        for label in labels:
            try:
                values.append(float(label.label_value))
            except (TypeError, ValueError):
                continue
        return values

    @staticmethod
    def _parse_json(payload: Optional[str]) -> Any:
        if not payload:
            return None
        try:
            return json.loads(payload)
        except Exception:  # noqa: BLE001
            return payload
