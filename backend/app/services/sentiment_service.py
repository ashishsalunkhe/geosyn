from typing import List
from app.models.domain import Document, EventCluster
from app.pipelines.normalization import NormalizationPipeline

class SentimentService:
    def __init__(self):
        self.pipeline = NormalizationPipeline()
        # High intensity keywords
        self.intensity_markers = [
            "spike", "crash", "surge", "collapse", "crisis", 
            "unprecedented", "shock", "emergency", "military", "war"
        ]

    def calculate_intensity(self, text: str) -> float:
        """
        Calculates a narrative intensity score from 0.0 to 1.0.
        """
        text_lower = text.lower()
        score = 0.0
        
        # Count intensity markers
        marker_count = sum(1 for marker in self.intensity_markers if marker in text_lower)
        
        # Count themes
        themes = self.pipeline.extract_entities(text)
        theme_count = len(themes)
        
        # Simple weighted sum
        score = (marker_count * 0.15) + (theme_count * 0.1)
        return min(score, 1.0)

    def get_event_intensity(self, event: EventCluster, documents: List[Document]) -> float:
        """
        Aggregates intensity across all documents in an event cluster.
        """
        if not documents:
            return 0.0
            
        scores = [self.calculate_intensity(doc.content) for doc in documents]
        # Average of the top 3 most intense documents to find the signal
        top_scores = sorted(scores, reverse=True)[:3]
        return sum(top_scores) / len(top_scores)
