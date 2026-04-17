from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.db.session import get_db
from app.models.brief_archive import IntelligenceArchive
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/trends")
def get_intelligence_trends(db: Session = Depends(get_db)):
    """
    Returns high-level trends from archived intelligence.
    - Most active topics
    - Average system confidence over time
    - Thematic intensity spikes
    """
    try:
        # 1. Top Topics
        top_topics = db.query(
            IntelligenceArchive.topic, 
            func.count(IntelligenceArchive.id).label("count")
        ).group_by(IntelligenceArchive.topic).order_by(func.count(IntelligenceArchive.id).desc()).limit(5).all()
        
        # 2. Confidence Trend (last 24 hours)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        confidence_points = db.query(
            IntelligenceArchive.created_at,
            IntelligenceArchive.total_confidence
        ).filter(IntelligenceArchive.created_at >= last_24h).order_by(IntelligenceArchive.created_at.asc()).all()
        
        # 3. Aggregate Thematic Dimensions & Geo Points
        archives = db.query(IntelligenceArchive).order_by(IntelligenceArchive.created_at.desc()).limit(10).all()
        thematic_agg = {
            "Military": 0, "Economic": 0, "Diplomatic": 0, "Logistic": 0, "Tech": 0
        }
        geo_points = []
        for arch in archives:
            if arch.thematic_weights:
                for k, v in arch.thematic_weights.items():
                    if k in thematic_agg:
                        thematic_agg[k] += v
            if arch.geo_points:
                geo_points.extend(arch.geo_points)

        return {
            "top_topics": [{"topic": t[0], "count": t[1]} for t in top_topics],
            "confidence_trend": [{"t": p[0].isoformat(), "v": p[1]} for p in confidence_points],
            "thematic_dimensions": thematic_agg,
            "geo_points": geo_points[:50], # Limit to top 50 to prevent map overload
            "archive_count": db.query(IntelligenceArchive).count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{topic}")
def get_topic_history(topic: str, db: Session = Depends(get_db)):
    """
    Returns the historical journey of a specific intelligence topic.
    """
    try:
        archives = db.query(IntelligenceArchive).filter(
            IntelligenceArchive.topic == topic
        ).order_by(IntelligenceArchive.created_at.asc()).all()
        
        return [
            {
                "timestamp": a.created_at.isoformat(),
                "confidence": a.total_confidence,
                "summary": a.brief_data.get("narrative_summary"),
                "signal": a.brief_data.get("confidence_metadata", {}).get("total_score", 0)
            } for a in archives
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
