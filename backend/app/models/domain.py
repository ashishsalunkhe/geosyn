from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

# Junction table for Document <-> Entity
document_entity_association = Table(
    "document_entity",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id")),
    Column("entity_id", Integer, ForeignKey("entities.id")),
)

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    reliability_score = Column(Float, default=1.0)
    source_type = Column(String)  # news, social, youtube, etc.
    
    documents = relationship("Document", back_populates="source")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    external_id = Column(String, index=True)
    title = Column(String)
    content = Column(Text)
    url = Column(String)
    published_at = Column(DateTime)
    normalized_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)
    event_cluster_id = Column(Integer, ForeignKey("event_clusters.id"), nullable=True)

    source = relationship("Source", back_populates="documents")
    event_cluster = relationship("EventCluster", back_populates="documents")
    entities = relationship("Entity", secondary=document_entity_association, back_populates="documents")
    claims = relationship("Claim", back_populates="document")

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    entity_type = Column(String)  # Person, Org, Location, etc.
    metadata_info = Column(JSON)

    documents = relationship("Document", secondary=document_entity_association, back_populates="entities")

class EventCluster(Base):
    __tablename__ = "event_clusters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text)
    
    documents = relationship("Document", back_populates="event_cluster")
    claims = relationship("Claim", back_populates="event_cluster")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    event_cluster_id = Column(Integer, ForeignKey("event_clusters.id"), nullable=True)
    text = Column(Text)
    verdict = Column(String)  # supported, contradicted, mixed, unverified
    confidence_score = Column(Float)
    reasoning = Column(Text)

    document = relationship("Document", back_populates="claims")
    event_cluster = relationship("EventCluster", back_populates="claims")

class NarrativeFrame(Base):
    __tablename__ = "narrative_frames"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # escalation, de-escalation, etc.
    description = Column(Text)

class MarketSeries(Base):
    __tablename__ = "market_series"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    name = Column(String)
    asset_class = Column(String)
    
    points = relationship("MarketPoint", back_populates="series")

class MarketPoint(Base):
    __tablename__ = "market_points"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("market_series.id"))
    timestamp = Column(DateTime, index=True)
    value = Column(Float)
    volume = Column(Float, nullable=True)

    series = relationship("MarketSeries", back_populates="points")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # volatility, chatter_surge, narrative_shift
    severity = Column(String)  # low, medium, high, critical
    ticker = Column(String, index=True)
    title = Column(String)
    content = Column(Text)
    context_snippet = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)
    alert_payload = Column(JSON)  # Store price delta, mentions delta, etc.

class CausalNode(Base):
    __tablename__ = "causal_nodes"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String)  # event, asset, entity
    entity_id = Column(Integer)  # ID in corresponding table
    name = Column(String)
    importance = Column(Float, default=1.0)
    node_meta = Column(JSON)

class CausalEdge(Base):
    __tablename__ = "causal_edges"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("causal_nodes.id"))
    target_node_id = Column(Integer, ForeignKey("causal_nodes.id"))
    relation_type = Column(String)  # causes, impacts, correlates
    weight = Column(Float)  # -1.0 to 1.0 (Sentiment/Impact Polarity)
    evidence = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("CausalNode", foreign_keys=[source_node_id])
    target = relationship("CausalNode", foreign_keys=[target_node_id])
