import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.domain import EventCluster, Document, Alert, CausalNode
from app.ingestion.fred_provider import fred_provider
from app.utils.datalake_manager import datalake

class DivergenceService:
    """
    Detects statistical 'Reality Gaps' between narrative news sentiment 
    and institutional macro reality.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def analyze_causal_shocks(self):
        """
        Runs the divergence detection algorithm across all active anchors.
        """
        print("GeoSyn: Running Tactical Divergence Analysis...")
        
        # 1. Fetch Key Macro series for comparison
        macro_series = ["CHIPMIADJMEI", "GDPC1", "DCOILWTICO", "DFF"]
        
        for series_id in macro_series:
            self._analyze_series_divergence(series_id)

    def _analyze_series_divergence(self, series_id: str):
        """
        Compares a specific macro series against related news sentiment.
        """
        # Get historical points from FRED
        history = fred_provider.fetch_series(series_id, days=60)
        if len(history) < 10: return

        vals = [h["value"] for h in history if h["value"] is not None]
        if not vals: return
        
        # Calculate Macro Momentum (latest delta vs avg)
        avg_val = np.mean(vals)
        latest_val = vals[-1]
        macro_delta = (latest_val - avg_val) / avg_val if avg_val != 0 else 0
        
        # Find related EventClusters
        series_keywords = {
            "CHIPMIADJMEI": ["china", "manufacturing", "pmi", "industrial"],
            "GDPC1": ["gdp", "growth", "economy", "recession"],
            "DCOILWTICO": ["oil", "energy", "petroleum", "fuel"],
            "DFF": ["fed", "interest", "hiking", "rates", "powell"]
        }
        
        keywords = series_keywords.get(series_id, [])
        all_events = self.db.query(EventCluster).all()
        related_events = []
        
        for ev in all_events:
            title_lower = (ev.title or "").lower()
            if any(k in title_lower for k in keywords):
                related_events.append(ev)
        
        if not related_events:
            return

        for event in related_events:
            # Sentiment proxy calculation
            pos_markers = ["growth", "surge", "deal", "recovery", "strong"]
            neg_markers = ["crash", "drop", "sanction", "threat", "weak"]
            
            sent_score = 0
            doc_count = 0
            for doc in event.documents:
                doc_count += 1
                content = (doc.content or "").lower()
                for p in pos_markers: sent_score += content.count(p)
                for n in neg_markers: sent_score -= content.count(n)
            
            if doc_count == 0: continue
            norm_sentiment = sent_score / doc_count

            # Divergence Detection Logic
            if macro_delta < -0.03 and norm_sentiment > 1.0:
                self._create_shock_alert(
                    "CAUSAL_INVERSION",
                    f"Macro Inversion: {series_id}",
                    f"Industrial reality for {series_id} shows a {macro_delta*100:.1f}% divergence from bullish news sentiment.",
                    event,
                    "critical"
                )
            
            elif macro_delta < -0.05 and abs(norm_sentiment) < 0.5:
                self._create_shock_alert(
                    "MACRO_BLINDSIDE",
                    f"Macro Blindside: {series_id}",
                    f"Sharp contraction detected in {series_id} ({macro_delta*100:.1f}%) with no corresponding news coverage.",
                    event,
                    "high"
                )

    def _create_shock_alert(self, type: str, title: str, content: str, event: EventCluster, severity: str):
        existing = self.db.query(Alert).filter(
            Alert.title == title,
            Alert.created_at > datetime.utcnow() - timedelta(hours=12)
        ).first()
        
        if not existing:
            alert = Alert(
                type=type,
                severity=severity,
                ticker="GLOBAL",
                title=title,
                content=content,
                context_snippet=event.summary or event.title,
                alert_payload={
                    "event_id": event.id,
                    "shock_type": type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            self.db.add(alert)
            
            # Tag the corresponding CausalNode
            node = self.db.query(CausalNode).filter(
                CausalNode.entity_type == "event",
                CausalNode.entity_id == event.id
            ).first()
            
            if node:
                meta = node.node_meta or {}
                meta["shock_type"] = type
                meta["shock_timestamp"] = datetime.utcnow().isoformat()
                meta["shock_content"] = content
                node.node_meta = meta
            
            self.db.commit()
            print(f"GeoSyn Shock Detected: {title}")
