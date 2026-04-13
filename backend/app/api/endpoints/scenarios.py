from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.strategic_scenario import StrategicScenario, ScenarioStatus
from app.services.ingestion_service import IngestionService

router = APIRouter()

class ScenarioCreate(BaseModel):
    topic: str
    region: Optional[str] = "GLOBAL"
    sector: Optional[str] = "GENERAL"
    description: Optional[str] = None

class ScenarioUpdate(BaseModel):
    status: Optional[ScenarioStatus] = None
    risk_score: Optional[float] = None
    impact_magnitude: Optional[str] = None

@router.get("/", response_model=List[dict])
def list_scenarios(
    region: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all tracked tactical scenarios with optional region/sector filters."""
    query = db.query(StrategicScenario)
    if region and region != "GLOBAL":
        query = query.filter(StrategicScenario.region == region)
    if sector and sector != "GENERAL":
        query = query.filter(StrategicScenario.sector == sector)
    
    scenarios = query.order_by(StrategicScenario.last_signal_at.desc()).all()
    return [
        {
            "id": s.id,
            "topic": s.topic,
            "status": s.status,
            "region": s.region,
            "sector": s.sector,
            "risk_score": s.risk_score,
            "impact_magnitude": s.impact_magnitude,
            "last_signal_at": s.last_signal_at,
            "created_at": s.created_at
        } for s in scenarios
    ]

@router.post("/", response_model=dict)
def follow_scenario(request: ScenarioCreate, db: Session = Depends(get_db)):
    """Initialize persistent tracking for a new strategic topic."""
    # Check if already followed
    existing = db.query(StrategicScenario).filter(StrategicScenario.topic == request.topic).first()
    if existing:
        return {"status": "already_following", "id": existing.id}
    
    new_scenario = StrategicScenario(
        topic=request.topic,
        region=request.region,
        sector=request.sector,
        description=request.description
    )
    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)
    
    return {"status": "success", "id": new_scenario.id, "topic": new_scenario.topic}

@router.patch("/{scenario_id}", response_model=dict)
def update_scenario(scenario_id: int, update: ScenarioUpdate, db: Session = Depends(get_db)):
    """Update the tactical status or risk profile of a tracked scenario."""
    scenario = db.query(StrategicScenario).filter(StrategicScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if update.status:
        scenario.status = update.status.value
    if update.risk_score is not None:
        scenario.risk_score = update.risk_score
    if update.impact_magnitude:
        scenario.impact_magnitude = update.impact_magnitude
    
    scenario.last_signal_at = datetime.utcnow()
    db.commit()
    return {"status": "updated", "id": scenario.id}

@router.post("/run")
def run_scenario_sync(topic: str, db: Session = Depends(get_db)):
    """Legacy endpoint for immediate sync, updated to track in scenarios if missing."""
    service = IngestionService(db)
    
    # Ensure scenario is tracked
    existing = db.query(StrategicScenario).filter(StrategicScenario.topic == topic).first()
    if not existing:
        new_s = StrategicScenario(topic=topic)
        db.add(new_s)
        db.commit()

    # Trigger async-like sync
    from app.ingestion.gdelt_provider import GDELTProvider
    gdelt = GDELTProvider()
    docs = service.run_ingestion(gdelt, query=topic)
    
    return {
        "status": "success",
        "topic": topic,
        "signals_ingested": len(docs)
    }

@router.get("/trending", response_model=List[dict])
def get_trending_scenarios():
    """Returns mock 'Community' strategic priorities for the Discovery Grid."""
    return [
        {
            "id": "trend-1",
            "topic": "Arctic Sovereignty & Trade Routes",
            "status": "EMERGING",
            "region": "GLOBAL",
            "sector": "LOGISTICS",
            "risk_score": 0.45,
            "community_interest": "HIGH"
        },
        {
            "id": "trend-2",
            "topic": "Rare Earth Mineral Cartels",
            "status": "ACTIVE",
            "region": "APAC",
            "sector": "ENERGY",
            "risk_score": 0.68,
            "community_interest": "MEDIUM"
        },
        {
            "id": "trend-3",
            "topic": "Digital Sovereign Currency Wars",
            "status": "EMERGING",
            "region": "EMEA",
            "sector": "FINANCE",
            "risk_score": 0.32,
            "community_interest": "LOW"
        },
        {
            "id": "trend-4",
            "topic": "Subsea Data Cable Vulnerability",
            "status": "CRITICAL",
            "region": "AMER",
            "sector": "INFOTECH",
            "risk_score": 0.89,
            "community_interest": "HIGH"
        }
    ]

@router.get("/summary")
def get_portfolio_summary(db: Session = Depends(get_db)):
    """Calculates aggregated KPIs for the high-density dashboard strip."""
    scenarios = db.query(StrategicScenario).all()
    count = len(scenarios)
    
    if count == 0:
        return {
            "avg_fragility": 0,
            "total_signals": 0,
            "critical_count": 0,
            "avg_confidence": 0,
            "market_exposure": 0
        }
    
    # Aggregates
    critical_count = len([s for s in scenarios if s.status == "CRITICAL"])
    risk_sum = sum([s.risk_score for s in scenarios if s.risk_score])
    avg_risk = (risk_sum / count) * 100 if count > 0 else 0
    
    return {
        "avg_fragility": round(avg_risk, 1),
        "total_signals": count * 542 + 1204, # Mocked base + per scenario
        "critical_count": critical_count,
        "avg_confidence": 88.2,
        "market_exposure": round(avg_risk * 1.2, 1)
    }

