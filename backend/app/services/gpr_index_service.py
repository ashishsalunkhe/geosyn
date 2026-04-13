from typing import List, Dict, Any
import numpy as np

class GPRIndexService:
    """
    Implements quantitative indexing for geopolitical risk (GeoSyn Fragility Index).
    Calculates both Volume-based (mention frequency) and Intensity-based (tone-weighted) scores.
    """

    # GDELT themes that indicate high geopolitical friction
    FRAGILITY_THEMES = {
        "CRISISLEX_CONFLICT", "MILITARY", "ECON_WAR", "TERROR", 
        "REBELLION", "UNREST", "SANCTIONS", "BORDER_DISPUTE",
        "POLITICS_SCANDAL", "CYBER_ATTACK", "PROTEST"
    }

    @staticmethod
    def calculate_gfi(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main entry point for GFI calculation.
        """
        if not articles:
            return {
                "volume_index": 0,
                "intensity_index": 0,
                "aggregate_score": 0,
                "status": "STABLE"
            }

        total_count = len(articles)
        risk_articles = []
        
        for art in articles:
            themes = set(art.get("themes", []))
            # Check if any article theme matches our fragility list
            if themes.intersection(GPRIndexService.FRAGILITY_THEMES):
                risk_articles.append(art)

        # 1. Volume Index: (Risk Signals / Total Signals) * 100
        volume_idx = (len(risk_articles) / total_count) * 100

        # 2. Intensity Index: Average Tone of Risk Articles, normalized 0-100
        # GDELT Tone ranges -100 to +100. We care about the negative delta.
        tones = [float(art.get("tone", 0)) for art in risk_articles]
        if not tones:
            intensity_idx = 0
        else:
            # Map -20 (Very negative) to 100, and 0+ to 0.
            # We focus on the range [0, -20] for high friction OSINT.
            avg_tone = np.mean(tones)
            # intensity = max(0, min(100, abs(avg_tone) * 5))
            intensity_idx = max(0, min(100, (abs(avg_tone) / 20.0) * 100)) if avg_tone < 0 else 0

        # Aggregate: Simple average of Volume and Intensity
        aggregate = (volume_idx + intensity_idx) / 2

        status = "STABLE"
        if aggregate > 75: status = "CRITICAL"
        elif aggregate > 50: status = "VOLATILE"
        elif aggregate > 25: status = "UNSETTLED"

        return {
            "volume_index": round(volume_idx, 1),
            "intensity_index": round(intensity_idx, 1),
            "aggregate_score": round(aggregate, 1),
            "status": status,
            "sample_size": total_count
        }

    @staticmethod
    def extract_mesh_records(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts standardized mesh records for the 'Intelligence Ledger'.
        Similar to Taiyo's 'All Records' view.
        """
        mesh = []
        for i, art in enumerate(articles):
            # Deterministic ID for UI mapping
            record_id = f"GFI-{art.get('seendate', '0')[:8]}-{i:03d}"
            
            # Identify primary sector from themes
            themes = art.get("themes", [])
            primary_sector = "GENERAL"
            if any("ECON" in t for t in themes): primary_sector = "ECONOMY"
            elif any("MIL" in t for t in themes): primary_sector = "DEFENSE"
            elif any("TECH" in t for t in themes) or any("CYBER" in t for t in themes): primary_sector = "TECH"
            elif any("ENERGY" in t for t in themes): primary_sector = "ENERGY"

            mesh.append({
                "id": record_id,
                "source": art.get("source", "GLOBAL_NEWS"),
                "title": art.get("title", "Unknown Tactical Signal"),
                "url": art.get("url", "#"),
                "sector": primary_sector,
                "tone": float(art.get("tone", 0.0)),
                "reliability": 0.85 if "REUTERS" in art.get("source", "") or "BLOOMBERG" in art.get("source", "") else 0.70,
                "timestamp": art.get("seendate")
            })
        return mesh
