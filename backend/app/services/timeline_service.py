from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.models.brief_archive import IntelligenceArchive
from app.ingestion.gdelt_gkg_provider import GDELTGKGProvider
from app.services.correlation_service import CorrelationService
from app.services.llm_service import LLMService


class TimelineService:
    """
    Synthesizes multi-modal intelligence briefs and chronological causal chains.
    Uses GDELT GKG for real-time narrative signals.
    """
    
    def __init__(self):
        self.gkg_provider = GDELTGKGProvider()
        self.correlation_service = CorrelationService()
        self.llm_service = LLMService()

    def generate_intelligence_brief(self, topic: str, ticker: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Creates a data-rich brief: Timeline + Causal Chain + Market Correlation.
        Checks for cached results in IntelligenceArchive to avoid redundant API hits.
        """
        # 1. Check Cache (30-min tactical window)
        if db:
            cached = db.query(IntelligenceArchive).filter(
                IntelligenceArchive.topic == topic,
                IntelligenceArchive.ticker == ticker,
                IntelligenceArchive.expires_at > datetime.utcnow()
            ).order_by(IntelligenceArchive.created_at.desc()).first()
            
            if cached:
                print(f"GeoSyn: Cache HIT for topic '{topic}'. Serving from archive.")
                return cached.brief_data

        # 2. Cache MISS: Fetch historical/recent articles for the timeline
        print(f"GeoSyn: Cache MISS for topic '{topic}'. Fetching fresh signal from GDELT.")
        search_res = self.gkg_provider.fetch_enriched_brief(topic, limit=15, db=db)
        articles = search_res.get("articles", [])
        search_metadata = search_res.get("search_metadata", {})
        
        timeline = []
        theme_counts = {}
        for art in articles:
            # Aggregate themes for the Heatmap/Radar
            for theme in art.get("themes", []):
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

            # Normalize tone label
            tone = float(art.get("tone", 0))
            tone_label = "NEUTRAL"
            if tone < -20: tone_label = "HOSTILE"
            elif tone < -5: tone_label = "NEGATIVE"
            elif tone > 20: tone_label = "POSITIVE"
            elif tone > 5: tone_label = "ENCOURAGING"

            # Parse Date
            parsed_date = art.get("seendate") or datetime.utcnow().isoformat() + "Z"

            # Parse Source Domain
            publisher = art.get("source") or "Global Agency"
            source_url = art.get("url", "")

            timeline.append({
                "timestamp": parsed_date,
                "title": art.get("title", "Untitled"),
                "url": source_url,
                "source": publisher,
                "tone": tone,
                "tone_label": tone_label,
                "themes": art.get("themes", []),
                "entities": {
                    "organizations": art.get("organizations", []),
                    "locations": art.get("locations", [])
                }
            })

        # 3. Extract Causal Chain (Heuristic based on GKG V2 Themes)
        chain = self._synthesize_causal_chain(timeline)

        # 4. Correlation (if ticker provided)
        correlation = None
        if ticker:
            correlation = self.correlation_service.compute_narrative_market_correlation(topic, ticker)

        # 5. Possible Effects (Statistical projection)
        possible_effects = []
        if correlation and not correlation.get("error"):
            best_fit = correlation.get("best_fit")
            if best_fit and best_fit["is_significant"]:
                r = best_fit["r"]
                direction = "UP" if r > 0 else "DOWN"
                magnitude = "MODERATE" if abs(r) > 0.4 else "LOW"
                if abs(r) > 0.7: magnitude = "HIGH"
                
                possible_effects.append({
                    "asset": ticker,
                    "direction": direction,
                    "magnitude": magnitude,
                    "timeframe": f"{best_fit['lag_days']}-5 days",
                    "confidence": best_fit["r"],
                    "basis": f"Pearson r {best_fit['r']} with lag {best_fit['lag_days']}d"
                })

        # 6. LLM Enhancement (if available)
        llm_enhanced = False
        narrative_summary = None
        
        # Calculate Dynamic Confidence
        from app.services.confidence_engine import ConfidenceEngine
        confidence_meta = ConfidenceEngine.calculate_system_confidence(timeline, correlation)

        if self.llm_service.is_enabled and timeline:
            llm_brief = self.llm_service.synthesize_intelligence_brief(
                topic, 
                timeline, 
                {"correlation": correlation, "effects": possible_effects}
            )
            if llm_brief:
                llm_enhanced = True
                narrative_summary = llm_brief.get("narrative_summary")
                chain = llm_brief.get("causal_chain", chain)
                
                if llm_brief.get("strategic_outlook"):
                    possible_effects.insert(0, {
                        "asset": "STRATEGIC",
                        "direction": "OUTLOOK",
                        "basis": llm_brief["strategic_outlook"],
                        "category": "MACRO",
                        "confidence": confidence_meta["total_score"] / 100.0
                    })
                
                # Add asset-specific projections
                if llm_brief.get("market_projections"):
                    for proj in llm_brief["market_projections"]:
                        if isinstance(proj, dict):
                            possible_effects.append({
                                "asset": proj.get("asset", "Unknown"),
                                "ticker": proj.get("ticker", ticker),
                                "category": proj.get("category", "MACRO"),
                                "direction": proj.get("direction", "UNKNOWN"),
                                "magnitude": proj.get("magnitude", "LOW"),
                                "basis": proj.get("rationale", ""),
                                "confidence": proj.get("confidence_score", 0.75),
                                "justification": proj.get("justification", "Extracted via context synthesis")
                            })
                        elif isinstance(proj, str):
                            possible_effects.append({
                                "asset": ticker or "STRATEGIC",
                                "ticker": ticker,
                                "category": "MACRO",
                                "direction": "UNKNOWN",
                                "magnitude": "MODERATE",
                                "basis": proj,
                                "confidence": 0.5,
                                "justification": "Inferred from unstructured projection"
                            })

        # 7. GeoSyn 2.0 Enrichment (Index & Mesh)
        from app.services.gpr_index_service import GPRIndexService
        try:
            gfi_metrics = GPRIndexService.calculate_gfi(articles)
            standardized_mesh = GPRIndexService.extract_mesh_records(articles)
        except Exception as e:
            print(f"GeoSyn: GPR Enrichment failed ({e}). Providing graceful defaults.")
            gfi_metrics = {"aggregate_score": 0.0, "status": "UNKNOWN", "volume_index": 0, "intensity_index": 0.0, "trend": "FLAT"}
            standardized_mesh = []

        # 8. Fetch Geopolitical Intensity Points for the Heatmap
        geo_points = self.gkg_provider.fetch_geo_intensity(topic)

        result = {
            "topic": topic,
            "brief_timestamp": datetime.utcnow().isoformat(),
            "timeline": timeline,
            "causal_chain": chain,
            "correlation": correlation,
            "possible_effects": possible_effects,
            "llm_enhanced": llm_enhanced,
            "narrative_summary": narrative_summary,
            "confidence_metadata": confidence_meta,
            "search_metadata": search_metadata if 'search_metadata' in locals() else {"type": "CACHE_HIT"},
            "gfi_metrics": gfi_metrics,
            "standardized_mesh": standardized_mesh,
            "geo_points": geo_points
        }

        # 8. Archive Result
        if db:
            try:
                # Map GDELT themes to broad Radar dimensions
                thematic = {
                    "Military": sum(v for k, v in theme_counts.items() if "MIL" in k),
                    "Economic": sum(v for k, v in theme_counts.items() if "ECON" in k),
                    "Diplomatic": sum(v for k, v in theme_counts.items() if "RELATIONS" in k or "DIP" in k),
                    "Logistic": sum(v for k, v in theme_counts.items() if "TRADE" in k or "TRANSPORT" in k),
                    "Tech": sum(v for k, v in theme_counts.items() if "CYBER" in k or "TECH" in k)
                }
                
                archive_record = IntelligenceArchive.create_on_demand_expiry(
                    topic=topic,
                    ticker=ticker,
                    brief=result,
                    thematic=thematic,
                    geo=geo_points
                )
                db.add(archive_record)
                db.commit()
                print(f"GeoSyn: Intelligence Brief for '{topic}' archived successfully.")
            except Exception as e:
                print(f"GeoSyn Archive Error: {e}")
                db.rollback()

        return result

    def _synthesize_causal_chain(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Synthesizes a causal chain by mapping event flows.
        Placeholder for heuristic logic: Top 3 most intense events.
        """
        # Sort by timestamp
        sorted_events = sorted(timeline, key=lambda x: x["timestamp"])
        
        chain = []
        for i, event in enumerate(sorted_events[:3]): # Simplify for the first few
            chain.append({
                "step": i + 1,
                "event": event["title"],
                "tone": event["tone"],
                "leads_to": f"Potential shift in {', '.join(event['themes'][:2])}" if event["themes"] else "Market sentiment shift",
                "evidence_count": len(timeline)
            })
        return chain
