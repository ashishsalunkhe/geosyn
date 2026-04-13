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
