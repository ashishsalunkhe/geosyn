from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Enum
from datetime import datetime
import enum
from app.db.base import Base

class ScenarioStatus(str, enum.Enum):
    EMERGING = "EMERGING"
    ACTIVE = "ACTIVE"
    CRITICAL = "CRITICAL"
    RESOLVING = "RESOLVING"
    STABILIZED = "STABILIZED"

class StrategicScenario(Base):
    """
    Persistent tactical scenario tracking (Taiyo-style).
    Transfers ephemeral searches into long-term strategic monitorings.
    """
    __tablename__ = "strategic_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True, unique=True)
    description = Column(String, nullable=True)
    status = Column(String, default=ScenarioStatus.EMERGING.value)
    
    region = Column(String, index=True, default="GLOBAL")  # APAC, EMEA, MENA, AMER
    sector = Column(String, index=True, default="GENERAL") # Defense, Tech, Energy
    
    risk_score = Column(Float, default=0.5)
    impact_magnitude = Column(String, default="MODERATE") # LOW, MODERATE, HIGH, EXTREME
    
    last_signal_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Store aggregated KPI data (for HUD trends)
    metrics_cache = Column(JSON, nullable=True)  # { "signal_count": 42, "trend": [0.1, 0.4...] }
    
    @classmethod
    def create_from_topic(cls, topic, region="GLOBAL", sector="GENERAL"):
        return cls(
            topic=topic,
            region=region,
            sector=sector,
            status=ScenarioStatus.EMERGING.value
        )
