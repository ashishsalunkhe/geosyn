import httpx
from typing import List, Dict, Any
from datetime import datetime
from app.ingestion.base import BaseProvider
from app.core.config import settings

class EventRegistryProvider(BaseProvider):
    def __init__(self):
        self.api_url = "http://eventregistry.org/api/v1/article/getArticles"
        self.api_key = settings.EVENT_REGISTRY_API_KEY

    @property
    def provider_name(self) -> str:
        return "Event Registry tactical"

    @property
    def source_type(self) -> str:
        return "news_api"

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Fetches latest geopolitical news from Event Registry (NewsAPI.ai).
        """
        if not self.api_key:
            print("Event Registry Error: No API Key configured.")
            return []

        search_query = query if query else "geopolitics conflict sanctions diplomacy"
        
        # Event Registry parameters
        params = {
            "action": "getArticles",
            "keyword": search_query,
            "articlesPage": 1,
            "articlesCount": 15,
            "articlesSortBy": "date",
            "dataType": ["news", "pr"],
            "forceMaxDataTime": True,
            "resultType": "articles",
            "apiKey": self.api_key
        }
        
        try:
            response = httpx.get(self.api_url, params=params, timeout=15.0)
            if response.status_code != 200:
                print(f"Event Registry Error: {response.status_code}")
                return []
            
            data = response.json()
            articles = data.get("articles", {}).get("results", [])
            
            raw_docs = []
            for art in articles:
                raw_docs.append({
                    "id": art.get("uri"),
                    "headline": art.get("title", "Untitled"),
                    "body": art.get("body", ""),
                    "url": art.get("url"),
                    "date": art.get("dateTimePub", datetime.utcnow().isoformat()),
                    "socialimage": art.get("image", ""),
                    "source_name": art.get("source", {}).get("title", "Global Intelligence")
                })
            return raw_docs
        except Exception as e:
            print(f"Event Registry Fetch Failed: {e}")
            return []
