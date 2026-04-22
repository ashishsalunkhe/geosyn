from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any
from datetime import datetime

# Base Schemas
class SourceBase(BaseModel):
    name: str
    url: Optional[str] = None
    reliability_score: float = 1.0
    source_type: str

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    content: str
    url: Optional[str] = None
    published_at: datetime
    external_id: str
    raw_data: Optional[Any] = None

class DocumentCreate(DocumentBase):
    source_id: int

class Document(DocumentBase):
    id: int
    source_id: int
    event_cluster_id: Optional[int] = None
    normalized_at: datetime

    class Config:
        from_attributes = True

class EntityBase(BaseModel):
    name: str
    entity_type: str
    metadata_info: Optional[Any] = None

class EntityCreate(EntityBase):
    pass

class Entity(EntityBase):
    id: int

    class Config:
        from_attributes = True

class EventClusterBase(BaseModel):
    title: str
    description: str
    summary: Optional[str] = None

class EventClusterCreate(EventClusterBase):
    pass

class EventCluster(EventClusterBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ClaimBase(BaseModel):
    text: str
    verdict: str # supported, contradicted, mixed, unverified
    confidence_score: float
    reasoning: Optional[str] = None

class ClaimCreate(ClaimBase):
    document_id: int
    event_cluster_id: Optional[int] = None

class Claim(ClaimBase):
    id: int
    document_id: int
    event_cluster_id: Optional[int] = None

    class Config:
        from_attributes = True

class MarketPointBase(BaseModel):
    timestamp: datetime
    value: float
    volume: Optional[float] = None

class MarketPointCreate(MarketPointBase):
    series_id: int

class MarketPoint(MarketPointBase):
    id: int
    series_id: int

    class Config:
        from_attributes = True

class MarketSeriesBase(BaseModel):
    ticker: str
    name: str
    asset_class: str

class MarketSeriesCreate(MarketSeriesBase):
    pass

class MarketSeries(MarketSeriesBase):
    id: int
    points: List[MarketPoint] = []

    class Config:
        from_attributes = True


class EventV2Document(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    source_id: int
    is_primary: bool = False
    raw_payload_ref: Optional[str] = None
    source_confidence: Optional[float] = None


class EventV2Entity(BaseModel):
    id: str
    canonical_name: str
    display_name: Optional[str] = None
    entity_type: str
    event_role: Optional[str] = None


class EventV2WatchlistMatch(BaseModel):
    watchlist_id: str
    entity_id: Optional[str] = None
    item_type: str
    criticality_score: Optional[float] = None


class EventV2ExposureMatch(BaseModel):
    id: str
    source_object_type: str
    source_object_id: str
    source_object_name: Optional[str] = None
    relationship_type: str
    criticality_score: Optional[float] = None
    exposure_weight: Optional[float] = None
    confidence_score: Optional[float] = None
    target_entity_id: Optional[str] = None
    target_entity_name: Optional[str] = None
    metadata: Optional[Any] = None


class EventTimelineV2(BaseModel):
    id: int
    event_id: str
    occurred_at: Optional[datetime] = None
    title: str
    description: Optional[str] = None
    source_document_id: Optional[str] = None
    timeline_type: str
    metadata: Optional[Any] = None


class RiskScoreV2(BaseModel):
    id: str
    score_type: str
    score_value: float
    confidence_score: Optional[float] = None
    severity: str
    rationale_text: Optional[str] = None
    scored_at: Optional[datetime] = None
    metadata: Optional[Any] = None


class EvalLabelV2(BaseModel):
    id: str
    label_type: str
    label_value: str
    notes: Optional[str] = None
    labeled_by: Optional[str] = None
    labeled_at: datetime
    alert_id: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Optional[Any] = None


class EventV2Summary(BaseModel):
    id: str
    canonical_title: str
    event_type: Optional[str] = None
    event_subtype: Optional[str] = None
    status: str
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    severity_score: Optional[float] = None
    confidence_score: Optional[float] = None
    summary_text: Optional[str] = None
    document_count: int = 0
    entity_count: int = 0
    timeline_count: int = 0
    matched_watchlists: List[EventV2WatchlistMatch] = Field(default_factory=list)
    exposure_matches: List[EventV2ExposureMatch] = Field(default_factory=list)
    risk_score: Optional[RiskScoreV2] = None


class EventV2Detail(EventV2Summary):
    documents: List[EventV2Document] = Field(default_factory=list)
    entities: List[EventV2Entity] = Field(default_factory=list)
    timeline: List[EventTimelineV2] = Field(default_factory=list)
    exposure_summary: Optional[str] = None


class AlertV2Summary(BaseModel):
    id: str
    event_id: str
    alert_type: str
    severity: str
    status: str
    headline: str
    summary_text: Optional[str] = None
    recommended_action: Optional[str] = None
    triggered_at: datetime


class AlertV2Detail(AlertV2Summary):
    resolved_at: Optional[datetime] = None
    metadata: Optional[Any] = None


class AlertV2Evidence(BaseModel):
    document_id: int
    title: str
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    evidence_type: Optional[str] = None
    relevance_score: Optional[float] = None
