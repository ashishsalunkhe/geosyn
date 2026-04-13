import numpy as np
from typing import List, Dict, Any
from app.models.domain import Document

class ConfidenceEngine:
    """
    Calculates dynamic intelligence confidence scores based on:
    1. Data Volume (Evidence Density)
    2. Narrative Coherence (Tone Variance)
    3. Source Diversity
    4. Statistical Significance (Lead-Lag strength)
    """

    @staticmethod
    def calculate_system_confidence(articles: List[Dict[str, Any]], stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculates a confidence score from 0 to 100.
        """
        if not articles:
            return {"total_score": 0, "breakdown": {"volume": 0, "coherence": 0, "stats": 0}}

        # 1. Volume Score (Max 40 points)
        # We want at least 15 articles for a 'High' confidence brief.
        volume_score = min(len(articles) / 15, 1.0) * 40

        # 2. Narrative Coherence Score (Max 40 points)
        # Based on variance of 'tone' in articles.
        tones = [a.get("tone", 0) for a in articles]
        if len(tones) > 1:
            # We normalize tone variance. A variance of 25 (e.g. half -5, half +5) 
            # is a highly contested narrative.
            tone_variance = np.var(tones)
            # High variance reduces coherence score.
            # Max penalty at variance of 20.
            coherence_score = max(0, 1.0 - (tone_variance / 20.0)) * 40
        else:
            coherence_score = 20 # Neutrally confident with single source

        # 3. Statistical Support (Max 20 points)
        stats_score = 0
        if stats and not stats.get("error"):
            best_fit = stats.get("best_fit")
            if best_fit:
                # p-value < 0.05 gives 15 points, and r > 0.5 gives 5 more.
                if best_fit.get("p_value", 1.0) < 0.05:
                    stats_score += 15
                if abs(best_fit.get("r", 0)) > 0.5:
                    stats_score += 5
        
        total_score = round(volume_score + coherence_score + stats_score)
        
        return {
            "total_score": min(total_score, 100),
            "breakdown": {
                "evidence_density": round(volume_score),
                "narrative_coherence": round(coherence_score),
                "statistical_validation": round(stats_score)
            },
            "rationale": ConfidenceEngine._generate_rationale(total_score, len(articles), tones)
        }

    @staticmethod
    def _generate_rationale(score: int, count: int, tones: List[float]) -> str:
        if score > 85:
            return "HIGH: Strong source alignment and verified statistical correlations."
        elif score > 60:
            return "MODERATE: Sufficient evidence volume with minor narrative divergence."
        elif count < 5:
            return "LOW: Insufficient data density for high-fidelity inference."
        elif np.var(tones) > 10:
            return "CAUTION: Highly contested narrative detected with low coherence."
        return "STABLE: Standard data ingestion metrics."
