from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.core.metrics import request_cache_hits_total, request_cache_misses_total
from app.core.redis_client import cache_get_json, cache_set_json
from app.services.timeline_service import TimelineService
from app.services.explainability_service import ExplainabilityService
from app.ingestion.gdelt_gkg_provider import GDELTGKGProvider

router = APIRouter()

@router.get("/brief")
def get_intelligence_brief(
    topic: str = Query(..., description="Topic to analyze (e.g. 'sanctions')"),
    ticker: Optional[str] = Query(None, description="Optional asset ticker (e.g. 'CL=F')"),
    db: Session = Depends(get_db)
):
    """
    Returns a multi-modal intelligence brief: Timeline, Causal Chain, and Market Correlation.
    """
    try:
        service = TimelineService()
        return service.generate_intelligence_brief(topic, ticker, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.models.domain import Document, Source

@router.get("/live")
def get_live_intelligence(
    query: str = "geopolitics",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Returns a real-time feed of articles pulled locally from the RSS/OSINT ingestion graph.
    """
    try:
        cache_key = f"intelligence-live:{query}:{limit}"
        cached = cache_get_json(cache_key)
        if cached is not None:
            request_cache_hits_total.labels("intelligence.live").inc()
            return cached
        request_cache_misses_total.labels("intelligence.live").inc()

        # Use simple text matching for filtering
        query_terms = query.lower().replace("or", " ").replace("and", " ").split() if query else []
        
        # Pull latest documents globally
        docs = db.query(Document).order_by(Document.published_at.desc()).limit(limit * 3).all()
        
        results = []
        for d in docs:
            # Filter logically (simplified representation of SQL string matching)
            if query_terms:
                content_block = (d.title + " " + (d.content or "")).lower()
                if not any(term in content_block for term in query_terms if term):
                    continue
            
            source_name = "Global Monitor"
            if d.source:
                source_name = d.source.name
            
            results.append({
                "id": d.external_id,
                "title": d.title,
                "url": d.url,
                "source": source_name,
                "seendate": d.published_at.isoformat() + "Z",
                "tone": d.raw_data.get("tone", 0.0) if d.raw_data else 0.0,
                "themes": []
            })
            if len(results) >= limit:
                break
                
        # Heuristic padding: guarantee UI never starves. If < limit elements, pad with latest global news.
        if len(results) < limit and docs:
            existing_ids = {r["id"] for r in results}
            for d in docs:
                if len(results) >= limit: break
                if d.external_id in existing_ids: continue
                
                source_name = d.source.name if d.source else "Global Monitor"
                results.append({
                    "id": d.external_id,
                    "title": d.title,
                    "url": d.url,
                    "source": source_name,
                    "seendate": d.published_at.isoformat() + "Z",
                    "tone": d.raw_data.get("tone", 0.0) if d.raw_data else 0.0,
                    "themes": ["GLOBAL_MACRO"]
                })
                
        results.sort(key=lambda x: x["seendate"], reverse=True)
        cache_set_json(cache_key, results, ttl_seconds=120)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explain/{alert_id}")
def get_alert_explanation(alert_id: int, db: Session = Depends(get_db)):
    """
    Explains a specific alert using causal evidence.
    """
    try:
        service = ExplainabilityService(db)
        return service.explain_alert(alert_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
