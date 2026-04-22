from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def _uuid_str() -> str:
    return str(uuid4())


class EntityV2(Base):
    __tablename__ = "entities_v2"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    legacy_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, unique=True, index=True)
    entity_type = Column(String, nullable=False, index=True)
    canonical_name = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    country_code = Column(String, nullable=True, index=True)
    region_code = Column(String, nullable=True, index=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    legacy_entity = relationship("Entity")
    aliases = relationship("EntityAliasV2", back_populates="entity", cascade="all, delete-orphan")


class EventV2(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    canonical_title = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=True, index=True)
    event_subtype = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="emerging", index=True)
    first_seen_at = Column(DateTime, nullable=False, index=True)
    last_seen_at = Column(DateTime, nullable=False, index=True)
    primary_geo_entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True)
    severity_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    summary_text = Column(Text, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    primary_geo_entity = relationship("EntityV2")
    evidence = relationship("EventEvidenceV2", back_populates="event", cascade="all, delete-orphan")
    entities = relationship("EventEntityV2", back_populates="event", cascade="all, delete-orphan")
    timelines = relationship("EventTimelineV2", back_populates="event", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScoreV2", back_populates="event", cascade="all, delete-orphan")
    evaluation_labels = relationship("EvalLabelV2", back_populates="event", cascade="all, delete-orphan")


class EventEvidenceV2(Base):
    __tablename__ = "event_evidence"
    __table_args__ = (
        UniqueConstraint("event_id", "legacy_document_id", name="uq_event_evidence_event_legacy_document"),
    )

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    legacy_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    contribution_type = Column(String, nullable=True)
    relevance_score = Column(Float, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("EventV2", back_populates="evidence")
    legacy_document = relationship("Document")


class EventEntityV2(Base):
    __tablename__ = "event_entities"
    __table_args__ = (
        UniqueConstraint("event_id", "entity_id", "event_role", name="uq_event_entities_event_entity_role"),
    )

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=False, index=True)
    event_role = Column(String, nullable=True, index=True)
    confidence_score = Column(Float, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("EventV2", back_populates="entities")
    entity = relationship("EntityV2")


class EventTimelineV2(Base):
    __tablename__ = "event_timelines"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    occurred_at = Column(DateTime, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source_document_id = Column(String(36), ForeignKey("evidence_documents.id"), nullable=True, index=True)
    timeline_type = Column(String, nullable=False, index=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("EventV2", back_populates="timelines")
    source_document = relationship("EvidenceDocumentV2")


class LegacyClusterEventMapV2(Base):
    __tablename__ = "legacy_cluster_event_map"

    legacy_cluster_id = Column(Integer, ForeignKey("event_clusters.id"), primary_key=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, unique=True, index=True)
    migrated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    legacy_cluster = relationship("EventCluster")
    event = relationship("EventV2")


class CustomerV2(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    industry = Column(String, nullable=True, index=True)
    primary_region = Column(String, nullable=True, index=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    watchlists = relationship("WatchlistV2", back_populates="customer", cascade="all, delete-orphan")
    assets = relationship("CustomerAssetV2", back_populates="customer", cascade="all, delete-orphan")


class WatchlistV2(Base):
    __tablename__ = "watchlists"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    watchlist_type = Column(String, nullable=True, index=True)
    is_default = Column(Boolean, default=False, nullable=False)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2", back_populates="watchlists")
    items = relationship("WatchlistItemV2", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItemV2(Base):
    __tablename__ = "watchlist_items"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    watchlist_id = Column(String(36), ForeignKey("watchlists.id"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, index=True)
    item_type = Column(String, nullable=False, index=True)
    criticality_score = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    watchlist = relationship("WatchlistV2", back_populates="items")
    entity = relationship("EntityV2")


class ExposureLinkV2(Base):
    __tablename__ = "exposure_links"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    source_object_type = Column(String, nullable=False, index=True)
    source_object_id = Column(String(64), nullable=False, index=True)
    target_entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, index=True)
    relationship_type = Column(String, nullable=False, index=True)
    criticality_score = Column(Float, nullable=True)
    exposure_weight = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2")
    target_entity = relationship("EntityV2")


class SupplierV2(Base):
    __tablename__ = "suppliers"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, index=True)
    supplier_name = Column(String, nullable=False, index=True)
    tier_level = Column(Integer, nullable=True)
    country_code = Column(String, nullable=True, index=True)
    criticality_score = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2")
    entity = relationship("EntityV2")


class FacilityV2(Base):
    __tablename__ = "facilities"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, index=True)
    facility_name = Column(String, nullable=False, index=True)
    facility_type = Column(String, nullable=True, index=True)
    country_code = Column(String, nullable=True, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    criticality_score = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2")
    entity = relationship("EntityV2")


class AlertV2(Base):
    __tablename__ = "alerts_v2"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    alert_type = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="new", index=True)
    headline = Column(String, nullable=False)
    summary_text = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2")
    event = relationship("EventV2")
    evidence = relationship("AlertEvidenceV2", back_populates="alert", cascade="all, delete-orphan")
    actions = relationship("AlertActionV2", back_populates="alert", cascade="all, delete-orphan")


class AlertEvidenceV2(Base):
    __tablename__ = "alert_evidence"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), ForeignKey("alerts_v2.id"), nullable=False, index=True)
    legacy_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    evidence_type = Column(String, nullable=True)
    relevance_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    alert = relationship("AlertV2", back_populates="evidence")
    legacy_document = relationship("Document")


class AlertActionV2(Base):
    __tablename__ = "alert_actions"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), ForeignKey("alerts_v2.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False, index=True)
    actor_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    alert = relationship("AlertV2", back_populates="actions")


class IngestSourceV2(Base):
    __tablename__ = "ingest_sources"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    legacy_source_id = Column(Integer, ForeignKey("sources.id"), nullable=True, unique=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    source_type = Column(String, nullable=False, index=True)
    source_tier = Column(String, nullable=True, index=True)
    base_url = Column(String, nullable=True)
    country_code = Column(String, nullable=True, index=True)
    language_code = Column(String, nullable=True, index=True)
    reliability_score = Column(Float, nullable=True)
    license_class = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    legacy_source = relationship("Source")
    documents = relationship("EvidenceDocumentV2", back_populates="source", cascade="all, delete-orphan")


class EvidenceDocumentV2(Base):
    __tablename__ = "evidence_documents"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_evidence_documents_source_external_id"),
    )

    id = Column(String(36), primary_key=True, default=_uuid_str)
    legacy_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True, unique=True, index=True)
    source_id = Column(String(36), ForeignKey("ingest_sources.id"), nullable=False, index=True)
    external_id = Column(String, nullable=True)
    canonical_url = Column(String, nullable=True)
    title = Column(String, nullable=False, index=True)
    body_text = Column(Text, nullable=True)
    summary_text = Column(Text, nullable=True)
    language_code = Column(String, nullable=True, index=True)
    country_code = Column(String, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    event_time = Column(DateTime, nullable=True, index=True)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    content_hash = Column(String, nullable=True, index=True)
    raw_payload_ref = Column(String, nullable=True)
    source_confidence = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)

    source = relationship("IngestSourceV2", back_populates="documents")
    legacy_document = relationship("Document")
    fragments = relationship("DocumentFragmentV2", back_populates="document", cascade="all, delete-orphan")
    entities = relationship("DocumentEntityV2", back_populates="document", cascade="all, delete-orphan")


class DocumentFragmentV2(Base):
    __tablename__ = "document_fragments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("evidence_documents.id"), nullable=False, index=True)
    fragment_type = Column(String, nullable=False, index=True)
    fragment_text = Column(Text, nullable=False)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("EvidenceDocumentV2", back_populates="fragments")


class DocumentEntityV2(Base):
    __tablename__ = "document_entities"
    __table_args__ = (
        UniqueConstraint("document_id", "entity_id", "mention_text", name="uq_document_entities_doc_entity_mention"),
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("evidence_documents.id"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=False, index=True)
    mention_text = Column(String, nullable=True)
    mention_role = Column(String, nullable=True, index=True)
    confidence_score = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("EvidenceDocumentV2", back_populates="entities")
    entity = relationship("EntityV2")


class EntityAliasV2(Base):
    __tablename__ = "entity_aliases"
    __table_args__ = (
        UniqueConstraint("entity_id", "alias", name="uq_entity_aliases_entity_alias"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=False, index=True)
    alias = Column(String, nullable=False, index=True)
    alias_type = Column(String, nullable=True, index=True)
    language_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    entity = relationship("EntityV2", back_populates="aliases")


class EntityRelationshipV2(Base):
    __tablename__ = "entity_relationships"
    __table_args__ = (
        UniqueConstraint(
            "source_entity_id",
            "target_entity_id",
            "relationship_type",
            name="uq_entity_relationships_edge",
        ),
    )

    id = Column(String(36), primary_key=True, default=_uuid_str)
    source_entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=False, index=True)
    target_entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=False, index=True)
    relationship_type = Column(String, nullable=False, index=True)
    weight = Column(Float, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    source_document_id = Column(String(36), ForeignKey("evidence_documents.id"), nullable=True, index=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_entity = relationship("EntityV2", foreign_keys=[source_entity_id])
    target_entity = relationship("EntityV2", foreign_keys=[target_entity_id])
    source_document = relationship("EvidenceDocumentV2")


class PortV2(Base):
    __tablename__ = "ports"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, unique=True, index=True)
    port_code = Column(String, nullable=True, unique=True, index=True)
    port_name = Column(String, nullable=False, index=True)
    country_code = Column(String, nullable=True, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    entity = relationship("EntityV2")


class RouteV2(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, unique=True, index=True)
    route_name = Column(String, nullable=False, index=True)
    route_type = Column(String, nullable=True, index=True)
    origin_port_id = Column(String(36), ForeignKey("ports.id"), nullable=True, index=True)
    destination_port_id = Column(String(36), ForeignKey("ports.id"), nullable=True, index=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    entity = relationship("EntityV2")
    origin_port = relationship("PortV2", foreign_keys=[origin_port_id])
    destination_port = relationship("PortV2", foreign_keys=[destination_port_id])


class CommodityV2(Base):
    __tablename__ = "commodities"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, unique=True, index=True)
    commodity_code = Column(String, nullable=True, unique=True, index=True)
    commodity_name = Column(String, nullable=False, index=True)
    sector = Column(String, nullable=True, index=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    entity = relationship("EntityV2")


class CustomerAssetV2(Base):
    __tablename__ = "customer_assets"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities_v2.id"), nullable=True, index=True)
    asset_label = Column(String, nullable=False, index=True)
    asset_type = Column(String, nullable=True, index=True)
    criticality_score = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2", back_populates="assets")
    entity = relationship("EntityV2")


class RiskScoreV2(Base):
    __tablename__ = "risk_scores"
    __table_args__ = (
        UniqueConstraint("event_id", "customer_id", "score_type", name="uq_risk_scores_event_customer_type"),
    )

    id = Column(String(36), primary_key=True, default=_uuid_str)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    score_type = Column(String, nullable=False, default="event_exposure", index=True)
    score_value = Column(Float, nullable=False, index=True)
    confidence_score = Column(Float, nullable=True)
    severity = Column(String, nullable=False, index=True)
    rationale_text = Column(Text, nullable=True)
    scored_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata_json = Column("metadata", Text, nullable=True)

    event = relationship("EventV2", back_populates="risk_scores")
    customer = relationship("CustomerV2")


class EvalLabelV2(Base):
    __tablename__ = "evaluation_labels"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True, index=True)
    alert_id = Column(String(36), ForeignKey("alerts_v2.id"), nullable=True, index=True)
    label_type = Column(String, nullable=False, index=True)
    label_value = Column(String, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    labeled_by = Column(String, nullable=True)
    labeled_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata_json = Column("metadata", Text, nullable=True)

    event = relationship("EventV2", back_populates="evaluation_labels")
    customer = relationship("CustomerV2")
    alert = relationship("AlertV2")


class BacktestRunV2(Base):
    __tablename__ = "backtest_runs"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    run_name = Column(String, nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True, index=True)
    config_json = Column("config", Text, nullable=True)
    metrics_json = Column("metrics", Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    status = Column(String, nullable=False, default="completed", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerV2")
