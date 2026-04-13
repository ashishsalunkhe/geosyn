from typing import Dict, Any, List
from datetime import datetime
from app.schemas.domain import DocumentCreate

class NormalizationPipeline:
    def __init__(self):
        # Keywords for theme detection (rule-based first pass)
        self.geopolitical_themes = [
            "sanctions", "alliance", "border", "escalation", 
            "de-escalation", "humanitarian", "energy", "shipping", 
            "refugees", "crisis", "security", "trade", "inflation",
            "interest rates", "monetary policy", "defense"
        ]
        self.geopolitical_actors = [
            "USA", "EU", "OPEC", "Russia", "NATO", "China", "India", 
            "RBI", "BSE", "NIFTY", "BRICS", "UN", "IMF", "Fed"
        ]

    def normalize(self, raw_doc: Dict[str, Any], source_id: int) -> DocumentCreate:
        """
        Transforms raw dictionary into DocumentCreate schema.
        Maps fields and performs basic cleaning.
        """
        # Mapping for MockNewsProvider (can be extended with provider-specific logic)
        return DocumentCreate(
            title=raw_doc.get("title", raw_doc.get("headline", "Untitled")),
            content=raw_doc.get("content", raw_doc.get("body", "")),
            url=raw_doc.get("url"),
            published_at=datetime.fromisoformat(raw_doc.get("seendate", raw_doc.get("date")).replace("Z", "+00:00")) if raw_doc.get("seendate") or raw_doc.get("date") else datetime.utcnow(),
            external_id=raw_doc.get("id", raw_doc.get("url", "")),
            source_id=source_id,
            raw_data=raw_doc
        )

    def extract_entities(self, content: str) -> List[Dict[str, str]]:
        """
        Extracts structured entities (themes and actors) from the content.
        """
        entities = []
        content_lower = content.lower()
        
        # Extract themes
        for theme in self.geopolitical_themes:
            if theme in content_lower:
                entities.append({"name": theme.capitalize(), "type": "Theme"})
        
        # Extract actors
        for actor in self.geopolitical_actors:
            if actor.lower() in content_lower:
                entities.append({"name": actor, "type": "Actor"})
                
        return entities
