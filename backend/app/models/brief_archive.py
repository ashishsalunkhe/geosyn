from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from datetime import datetime, timedelta
from app.db.base import Base

class IntelligenceArchive(Base):
    """
    Persists synthesized intelligence briefs to reduce API hits and track trends.
    """
    __tablename__ = "intelligence_archive"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    ticker = Column(String, index=True, nullable=True)
    
    # The full synthesized JSON (Timeline, Causal, Market, Thematic)
    brief_data = Column(JSON)
    
    # Advanced metadata for analytics
    total_confidence = Column(Float)
    thematic_weights = Column(JSON) # {Military: 0.8, Econ: 0.2...}
    geo_points = Column(JSON) # GeoJSON for mapping
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @classmethod
    def create_on_demand_expiry(cls, topic, brief, thematic=None, geo=None, ticker=None, minutes=30):
        """Helper to create a record with a specific TTL."""
        return cls(
            topic=topic,
            ticker=ticker,
            brief_data=brief,
            total_confidence=brief.get("confidence_metadata", {}).get("total_score", 0) / 100.0,
            thematic_weights=thematic,
            geo_points=geo,
            expires_at=datetime.utcnow() + timedelta(minutes=minutes)
        )
