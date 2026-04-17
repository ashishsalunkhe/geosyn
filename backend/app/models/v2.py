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
