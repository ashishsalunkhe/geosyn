from typing import List, Any, Dict
from datetime import datetime
from app.ingestion.base import BaseProvider

class YouTubeProvider(BaseProvider):
    def __init__(self, url: str):
        self.url = url

    @property
    def provider_name(self) -> str:
        return f"YouTube: {self.url.split('=')[-1]}"

    @property
    def source_type(self) -> str:
        return "youtube"

    def fetch_raw_docs(self) -> List[Dict[str, Any]]:
        # Mocking YouTube metadata and transcript extraction
        return [
            {
                "id": f"yt_{self.url.split('=')[-1]}",
                "headline": "Analyzing Recent Geopolitical Shocks",
                "body": "CLAIM: The new maritime alliance will lead to a 20% increase in regional shipping costs. EVIDENCE: Logistics experts point to increased insurance premiums and protective escorts.",
                "url": self.url,
                "date": datetime.utcnow().isoformat(),
                "author": "GlobalInsight TV",
                "transcript": "In today's video, we discuss the maritime alliance. CLAIM: It will cause a spike in costs. This is because of insurance premiums..."
            }
        ]
