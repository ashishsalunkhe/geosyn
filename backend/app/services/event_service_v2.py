from datetime import datetime
import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.domain import Document, Entity, EventCluster
from app.models.v2 import (
    CommodityV2,
    CustomerAssetV2,
    EntityV2,
    EvidenceDocumentV2,
    EventEntityV2,
    EventEvidenceV2,
    EventV2,
    ExposureLinkV2,
    FacilityV2,
    LegacyClusterEventMapV2,
    PortV2,
    RiskScoreV2,
    RouteV2,
    SupplierV2,
    WatchlistV2,
    WatchlistItemV2,
)
from app.services.provenance_service_v2 import ProvenanceServiceV2
from app.services.risk_scoring_service_v2 import RiskScoringServiceV2
from app.services.event_timeline_service_v2 import EventTimelineServiceV2


class EventServiceV2:
    def __init__(self, db: Session):
        self.db = db
        self.provenance_service = ProvenanceServiceV2(db)
        self.risk_service = RiskScoringServiceV2(db)
        self.timeline_service = EventTimelineServiceV2(db)

    def list_events(self, limit: int = 100, skip: int = 0) -> List[EventV2]:
        return (
            self.db.query(EventV2)
            .order_by(EventV2.last_seen_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_event(self, event_id: str) -> Optional[EventV2]:
        return self.db.query(EventV2).filter(EventV2.id == event_id).first()

    def get_event_by_legacy_cluster_id(self, legacy_cluster_id: int) -> Optional[EventV2]:
        mapping = (
            self.db.query(LegacyClusterEventMapV2)
            .filter(LegacyClusterEventMapV2.legacy_cluster_id == legacy_cluster_id)
            .first()
        )
        if not mapping:
            return None
        return self.get_event(mapping.event_id)

    def ensure_entity_v2(self, legacy_entity: Entity) -> EntityV2:
        existing = (
            self.db.query(EntityV2)
            .filter(EntityV2.legacy_entity_id == legacy_entity.id)
            .first()
        )
        if existing:
            return existing

        now = datetime.utcnow()
        entity = EntityV2(
            legacy_entity_id=legacy_entity.id,
            entity_type=(legacy_entity.entity_type or "unknown").lower(),
            canonical_name=legacy_entity.name,
            display_name=legacy_entity.name,
            created_at=now,
            updated_at=now,
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def ensure_event_for_cluster(self, cluster: EventCluster) -> EventV2:
        existing = self.get_event_by_legacy_cluster_id(cluster.id)
        now = datetime.utcnow()
        docs = sorted(
            cluster.documents,
            key=lambda d: d.published_at or cluster.created_at or now,
        )
        first_seen = docs[0].published_at if docs and docs[0].published_at else cluster.created_at or now
        last_seen = docs[-1].published_at if docs and docs[-1].published_at else first_seen

        if existing:
            existing.canonical_title = cluster.title or existing.canonical_title
            existing.summary_text = cluster.summary or cluster.description or existing.summary_text
            existing.first_seen_at = first_seen
            existing.last_seen_at = last_seen
            existing.updated_at = now
            self.db.flush()
            return existing

        event = EventV2(
            canonical_title=cluster.title or f"Cluster {cluster.id}",
            event_type="legacy_cluster",
            event_subtype=None,
            status="active",
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            summary_text=cluster.summary or cluster.description,
            created_at=now,
            updated_at=now,
        )
        self.db.add(event)
        self.db.flush()

        self.db.add(
            LegacyClusterEventMapV2(
                legacy_cluster_id=cluster.id,
                event_id=event.id,
                migrated_at=now,
            )
        )
        self.db.flush()
        return event

    def sync_document_to_cluster_event(self, doc: Document, cluster: EventCluster) -> EventV2:
        event = self.ensure_event_for_cluster(cluster)
        self.provenance_service.ensure_evidence_document(doc)
        self._attach_document_evidence(event, doc)
        self._attach_document_entities(event, doc)
        event.last_seen_at = max(event.last_seen_at or doc.published_at or datetime.utcnow(), doc.published_at or datetime.utcnow())
        event.updated_at = datetime.utcnow()
        self.db.flush()
        return event

    def sync_cluster(self, cluster: EventCluster) -> EventV2:
        event = self.ensure_event_for_cluster(cluster)
        for doc in cluster.documents:
            self.provenance_service.ensure_evidence_document(doc)
            self._attach_document_evidence(event, doc)
            self._attach_document_entities(event, doc)
        self.db.flush()
        return event

    def _attach_document_evidence(self, event: EventV2, doc: Document) -> None:
        existing = (
            self.db.query(EventEvidenceV2)
            .filter(
                EventEvidenceV2.event_id == event.id,
                EventEvidenceV2.legacy_document_id == doc.id,
            )
            .first()
        )
        if existing:
            return

        primary_doc = (
            self.db.query(EventEvidenceV2)
            .filter(EventEvidenceV2.event_id == event.id, EventEvidenceV2.is_primary == True)  # noqa: E712
            .first()
        )
        self.db.add(
            EventEvidenceV2(
                event_id=event.id,
                legacy_document_id=doc.id,
                contribution_type="cluster_sync",
                relevance_score=1.0,
                is_primary=primary_doc is None,
                created_at=datetime.utcnow(),
            )
        )

    def _attach_document_entities(self, event: EventV2, doc: Document) -> None:
        for legacy_entity in doc.entities:
            entity_v2 = self.ensure_entity_v2(legacy_entity)
            existing = (
                self.db.query(EventEntityV2)
                .filter(
                    EventEntityV2.event_id == event.id,
                    EventEntityV2.entity_id == entity_v2.id,
                    EventEntityV2.event_role == "mentioned",
                )
                .first()
            )
            if existing:
                continue
            self.db.add(
                EventEntityV2(
                    event_id=event.id,
                    entity_id=entity_v2.id,
                    event_role="mentioned",
                    confidence_score=1.0,
                    is_primary=False,
                    created_at=datetime.utcnow(),
                )
            )

    def serialize_event(self, event: EventV2, customer_id: Optional[str] = None) -> Dict[str, Any]:
        explanation = self.explain_event_for_customer(event.id, customer_id) if customer_id else None
        timelines = self.timeline_service.ensure_timelines_for_event(event)
        evidence = (
            self.db.query(EventEvidenceV2)
            .filter(EventEvidenceV2.event_id == event.id)
            .order_by(EventEvidenceV2.is_primary.desc(), EventEvidenceV2.created_at.asc())
            .all()
        )
        event_entities = (
            self.db.query(EventEntityV2)
            .filter(EventEntityV2.event_id == event.id)
            .all()
        )

        documents = []
        for row in evidence[:10]:
            doc = row.legacy_document
            evidence_doc = (
                self.db.query(EvidenceDocumentV2)
                .filter(EvidenceDocumentV2.legacy_document_id == doc.id)
                .first()
            )
            documents.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "url": doc.url,
                    "published_at": doc.published_at.isoformat() if doc.published_at else None,
                    "source_id": doc.source_id,
                    "is_primary": row.is_primary,
                    "raw_payload_ref": evidence_doc.raw_payload_ref if evidence_doc else None,
                    "source_confidence": evidence_doc.source_confidence if evidence_doc else None,
                }
            )

        entities = []
        for row in event_entities[:20]:
            entities.append(
                {
                    "id": row.entity.id,
                    "canonical_name": row.entity.canonical_name,
                    "display_name": row.entity.display_name,
                    "entity_type": row.entity.entity_type,
                    "event_role": row.event_role,
                }
            )

        risk_score = explanation["risk_score"] if explanation else None
        return {
            "id": event.id,
            "canonical_title": event.canonical_title,
            "event_type": event.event_type,
            "event_subtype": event.event_subtype,
            "status": event.status,
            "first_seen_at": event.first_seen_at.isoformat() if event.first_seen_at else None,
            "last_seen_at": event.last_seen_at.isoformat() if event.last_seen_at else None,
            "severity_score": event.severity_score,
            "confidence_score": event.confidence_score,
            "summary_text": event.summary_text,
            "document_count": len(evidence),
            "entity_count": len(event_entities),
            "timeline_count": len(timelines),
            "documents": documents,
            "entities": entities,
            "timeline": [self.timeline_service.serialize_timeline(row) for row in timelines[:20]],
            "matched_watchlists": explanation["matched_watchlists"] if explanation else [],
            "exposure_matches": explanation["exposure_matches"] if explanation else [],
            "exposure_summary": explanation["summary"] if explanation else None,
            "risk_score": risk_score,
        }

    def explain_event_for_customer(self, event_id: str, customer_id: Optional[str]) -> Dict[str, Any]:
        event = self.get_event(event_id)
        if not event or not customer_id:
            return {"event_id": event_id, "matched_watchlists": [], "exposure_matches": [], "summary": "No customer context available."}

        event_entities = (
            self.db.query(EventEntityV2)
            .filter(EventEntityV2.event_id == event.id)
            .all()
        )
        entity_ids = [row.entity_id for row in event_entities]
        matched_watchlists: List[Dict[str, Any]] = []
        exposure_matches: List[Dict[str, Any]] = []
        if entity_ids:
            watchlist_rows = (
                self.db.query(WatchlistItemV2)
                .join(WatchlistV2, WatchlistV2.id == WatchlistItemV2.watchlist_id)
                .filter(
                    WatchlistV2.customer_id == customer_id,
                    WatchlistItemV2.entity_id.in_(entity_ids),
                )
                .all()
            )
            for item in watchlist_rows:
                matched_watchlists.append(
                    {
                        "watchlist_id": item.watchlist_id,
                        "entity_id": item.entity_id,
                        "item_type": item.item_type,
                        "criticality_score": item.criticality_score,
                    }
                )

            exposure_rows = (
                self.db.query(ExposureLinkV2)
                .filter(
                    ExposureLinkV2.customer_id == customer_id,
                    ExposureLinkV2.target_entity_id.in_(entity_ids),
                )
                .order_by(ExposureLinkV2.criticality_score.desc(), ExposureLinkV2.exposure_weight.desc())
                .all()
            )
            for row in exposure_rows:
                source_object_name = self._resolve_source_object_name(row.source_object_type, row.source_object_id)
                exposure_matches.append(
                    {
                        "id": row.id,
                        "source_object_type": row.source_object_type,
                        "source_object_id": row.source_object_id,
                        "source_object_name": source_object_name,
                        "relationship_type": row.relationship_type,
                        "criticality_score": row.criticality_score,
                        "exposure_weight": row.exposure_weight,
                        "confidence_score": row.confidence_score,
                        "target_entity_id": row.target_entity_id,
                        "target_entity_name": row.target_entity.canonical_name if row.target_entity else None,
                        "metadata": self._parse_json(row.metadata_json),
                    }
                )

        summary = "No mapped customer exposure found for this event."
        if exposure_matches:
            top = exposure_matches[0]
            summary = (
                f"Event maps to customer exposure via {top['source_object_type']} "
                f"{top.get('source_object_name') or top['source_object_id']} through relationship '{top['relationship_type']}'."
            )
        elif matched_watchlists:
            top = matched_watchlists[0]
            summary = f"Event matches a customer watchlist item of type '{top['item_type']}'."

        risk_payload = None
        if customer_id:
            from app.models.v2 import CustomerV2

            customer = self.db.query(CustomerV2).filter(CustomerV2.id == customer_id).first()
            if customer:
                risk = self.risk_service.upsert_event_risk(
                    event,
                    customer,
                    explanation={
                        "matched_watchlists": matched_watchlists,
                        "exposure_matches": exposure_matches,
                        "document_count": self._event_document_count(event.id),
                    },
                )
                risk_payload = self.serialize_risk_score(risk)

        return {
            "event_id": event_id,
            "matched_watchlists": matched_watchlists,
            "exposure_matches": exposure_matches,
            "summary": summary,
            "risk_score": risk_payload,
        }

    def get_risk_score(self, event_id: str, customer_id: str) -> Optional[Dict[str, Any]]:
        risk = self.risk_service.get_event_risk(event_id, customer_id)
        return self.serialize_risk_score(risk) if risk else None

    @staticmethod
    def serialize_risk_score(risk: Optional[RiskScoreV2]) -> Optional[Dict[str, Any]]:
        if not risk:
            return None
        return {
            "id": risk.id,
            "score_type": risk.score_type,
            "score_value": risk.score_value,
            "confidence_score": risk.confidence_score,
            "severity": risk.severity,
            "rationale_text": risk.rationale_text,
            "scored_at": risk.scored_at.isoformat() if risk.scored_at else None,
            "metadata": EventServiceV2._parse_json(risk.metadata_json),
        }

    def _event_document_count(self, event_id: str) -> int:
        return (
            self.db.query(EventEvidenceV2)
            .filter(EventEvidenceV2.event_id == event_id)
            .count()
        )

    def _resolve_source_object_name(self, source_object_type: str, source_object_id: str) -> Optional[str]:
        mapping = {
            "supplier": (SupplierV2, "supplier_name"),
            "facility": (FacilityV2, "facility_name"),
            "port": (PortV2, "port_name"),
            "route": (RouteV2, "route_name"),
            "commodity": (CommodityV2, "commodity_name"),
            "customer_asset": (CustomerAssetV2, "asset_label"),
            "asset": (CustomerAssetV2, "asset_label"),
        }
        model_field = mapping.get(source_object_type.lower())
        if not model_field:
            return None
        model, field_name = model_field
        row = self.db.query(model).filter(model.id == source_object_id).first()
        return getattr(row, field_name, None) if row else None

    @staticmethod
    def _parse_json(payload: Optional[str]) -> Any:
        if not payload:
            return None
        try:
            return json.loads(payload)
        except Exception:  # noqa: BLE001
            return payload
