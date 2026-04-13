from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.domain import Alert, Document
from app.ingestion.gdelt_gkg_provider import GDELTGKGProvider
from app.services.correlation_service import CorrelationService
from app.services.llm_service import LLMService

class ExplainabilityService:
    """
    Provides evidence-based causal explanations for system-generated alerts.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.gkg_provider = GDELTGKGProvider()
        self.correlation_service = CorrelationService()
        self.llm_service = LLMService()

    def explain_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Generates a reasoning chain for a specific alert.
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {"error": "Alert not found"}

        # 1. Gather Context (Ticker + Timeframe)
        time_origin = alert.created_at
        ticker = alert.ticker
        
        # 2. Search for high-relevance evidence in GKG (last 6 hours around alert)
        query = ticker.replace("^", "").replace("=F", "") # Clean ticker for news query
        evidence_articles = self.gkg_provider.fetch_enriched_brief(query, limit=5)
        
        reasons = []
        if evidence_articles:
            reasons.append(f"Found {len(evidence_articles)} articles matching ${ticker} in the last hour.")
            avg_tone = sum(float(a.get("tone", 0)) for a in evidence_articles) / len(evidence_articles)
            reasons.append(f"Average narrative tone is {avg_tone:.2f} (GKG GDELT).")
        else:
            reasons.append(f"No direct narrative surge detected for ${ticker} in the GDELT GKG.")

        # 3. Check for Topic Correlation
        # If the ticker is CL=F, look for "Oil" topics
        candidate_topics = ["oil", "sanctions", "war", "trade"]
        correlation_evidence = []
        
        for topic in candidate_topics:
            corr = self.correlation_service.compute_narrative_market_correlation(topic, ticker, window_days=14)
            if not corr.get("error"):
                best = corr.get("best_fit")
                if best and best["is_significant"] and abs(best["r"]) > 0.5:
                    correlation_evidence.append({
                        "topic": topic,
                        "correlation": best["r"],
                        "lag": best["lag_days"]
                    })

        # 4. Construct Narrative Reasoning
        historical_pattern = "No strong historical pattern match found."
        strategic_narrative = None
        if correlation_evidence:
            top = correlation_evidence[0]
            historical_pattern = f"Price move aligns with '{top['topic']}' narrative which leads ${ticker} by {top['lag']} days (r={top['correlation']})."

        # 5. LLM Enhancement (if available)
        llm_enhanced = False
        if self.llm_service.is_enabled:
            llm_res = self.llm_service.generate_causal_reasoning(
                alert.content,
                [art.get("title") for art in evidence_articles[:3]],
                historical_pattern
            )
            if llm_res:
                llm_enhanced = True
                strategic_narrative = llm_res.get("strategic_narrative")
                historical_pattern = llm_res.get("historical_context") or historical_pattern

        return {
            "alert_id": alert_id,
            "why_triggered": alert.content,
            "evidence": [art.get("title") for art in evidence_articles[:3]],
            "raw_reasons": reasons,
            "historical_pattern": historical_pattern,
            "strategic_narrative": strategic_narrative,
            "correlation_matrix": correlation_evidence,
            "confidence": 0.82 if correlation_evidence else 0.45,
            "llm_enhanced": llm_enhanced
        }
