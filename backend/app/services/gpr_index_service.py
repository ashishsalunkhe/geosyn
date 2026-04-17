import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.domain import Document, EventCluster
from typing import Dict, Any, List

class GPRIndexService:
    """
    Implements the core logic for the Caldara & Iacoviello Geopolitical Risk (GPR) Index.
    
    The index is a ratio of 'Risk/Conflict' signals vs 'Baseline' coverage.
    Higher GPR levels indicate increasing systemic instability.
    """

    # Terms associated with geopolitical risk/threat as per institutional standards
    GPR_KEYWORDS = [
        "war", "conflict", "threat", "sanction", "military", "terror", "crisis",
        "attack", "missile", "invasion", "embargo", "geopolitical", "nuclear",
        "regime", "insurgency", "mobilization", "deployment", "blocking"
    ]

    def __init__(self, db: Session):
        self.db = db

    def calculate_rolling_gpr(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Calculates a daily GPR index for the last X days.
        Formula: (Count of Risk-Heavy Articles / Total Volume) * 100
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 1. Fetch documents in window
        docs = self.db.query(Document).filter(
            Document.published_at.between(start_date, end_date)
        ).all()
        
        if not docs:
            return []

        # 2. Group by Day
        days_data = {}
        for d in docs:
            day_str = d.published_at.strftime("%Y-%m-%d")
            if day_str not in days_data:
                days_data[day_str] = {"total": 0, "risk_hits": 0}
            
            days_data[day_str]["total"] += 1
            
            # Check for GPR keywords in content or title
            content_lower = (d.title + " " + (d.content or "")).lower()
            if any(k in content_lower for k in self.GPR_KEYWORDS):
                days_data[day_str]["risk_hits"] += 1

        # 3. Compute Normalized Index
        timeline = []
        # Sort by date
        sorted_days = sorted(days_data.keys())
        for day in sorted_days:
            counts = days_data[day]
            index_val = (counts["risk_hits"] / counts["total"]) * 100 if counts["total"] > 0 else 0
            timeline.append({
                "date": day,
                "gpr_score": round(index_val, 2),
                "total_articles": counts["total"],
                "risk_articles": counts["risk_hits"]
            })
            
        return timeline

    def get_current_gpr_level(self) -> float:
        """Returns the average GPR index for the last 48 hours."""
        recent = self.calculate_rolling_gpr(days=2)
        if not recent: return 0.0
        return round(np.mean([d["gpr_score"] for d in recent]), 2)
        
    @staticmethod
    def calculate_gfi(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates Geopolitical Fragility Index (GFI) metrics from a list of tactical articles.
        Returns score, trend, and status.
        """
        if not articles:
            return {"score": 0.0, "status": "STABLE", "trend": "FLAT"}

        risk_hits = 0
        total = len(articles)
        
        for art in articles:
            content = str(art.get("title", "")) + " " + str(art.get("themes", ""))
            content_lower = content.lower()
            if any(k in content_lower for k in GPRIndexService.GPR_KEYWORDS):
                risk_hits += 1

        raw_score = (risk_hits / total) * 100

        status = "STABLE"
        if raw_score >= 40:
            status = "CRITICAL"
        elif raw_score >= 15:
            status = "ELEVATED"

        return {
            "aggregate_score": round(raw_score, 2),
            "volume_index": total,
            "intensity_index": round((risk_hits / (total or 1)) * 50, 1),
            "status": status,
            "trend": "UP" if raw_score > 20 else "FLAT"
        }

    @staticmethod
    def extract_mesh_records(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts standardized mesh entities (locations, orgs) for the frontend graph.
        """
        mesh = []
        seen = set()
        for art in articles:
            # Support multiple data structures
            entities = art.get("entities", {})
            orgs = entities.get("organizations", []) if isinstance(entities, dict) else art.get("organizations", [])
            locs = entities.get("locations", []) if isinstance(entities, dict) else art.get("locations", [])
            
            # GDELT specific themes block
            if not orgs and "organizations" in art:
                orgs = art["organizations"]
            if not locs and "locations" in art:
                locs = art["locations"]

            for o in (orgs or []):
                o_str = str(o).strip()
                if o_str not in seen and len(o_str) > 2:
                    mesh.append({"entity": o_str, "type": "ORGANIZATION", "weight": 1})
                    seen.add(o_str)
                    
            for l in (locs or []):
                l_str = str(l).strip()
                if l_str not in seen and len(l_str) > 2:
                    mesh.append({"entity": l_str, "type": "LOCATION", "weight": 1})
                    seen.add(l_str)

        return mesh[:20]
