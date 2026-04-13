from typing import List, Any, Dict
from datetime import datetime
from app.ingestion.base import BaseProvider

class MockNewsProvider(BaseProvider):
    @property
    def provider_name(self) -> str:
        return "Global News Wire (Mock)"

    @property
    def source_type(self) -> str:
        return "news"

    def fetch_raw_docs(self) -> List[Dict[str, Any]]:
        # Simulated raw documents
        return [
            {
                "id": "mock_001",
                "headline": "New Sanctions Imposed on Energy Sector",
                "body": "Global powers have announced a fresh round of sanctions targeting maritime energy exports citing security concerns.",
                "url": "https://example.com/news/1",
                "date": datetime.utcnow().isoformat(),
                "author": "J. Doe"
            },
            {
                "id": "mock_002",
                "headline": "Maritime Alliance Grows in North Sea",
                "body": "Three additional nations have formally joined the regional security pact to protect vital shipping lanes.",
                "url": "https://example.com/news/2",
                "date": datetime.utcnow().isoformat(),
                "author": "A. Smith"
            },
            {
                "id": "mock_003",
                "headline": "Humanitarian Crisis Deepens at the Border",
                "body": "The flow of refugees has doubled over the last 48 hours as regional tensions continue to escalate.",
                "url": "https://example.com/news/3",
                "date": datetime.utcnow().isoformat(),
                "author": "L. Brown"
            }
        ]
