import httpx
from typing import List, Dict, Any
from datetime import datetime
from app.ingestion.base import BaseProvider

class GDELTProvider(BaseProvider):
    def __init__(self):
        self.api_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    @property
    def provider_name(self) -> str:
        return "GDELT Global Monitor"

    @property
    def source_type(self) -> str:
        return "news_api"

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Fetches latest geopolitical news from GDELT Doc API.
        """
        search_query = query if query else "geopolitics OR conflict OR sanctions OR diplomacy"
        params = {
            "query": search_query,
            "mode": "artlist",
            "maxresults": "15",
            "sort": "date",
            "format": "json"
        }
        
        try:
            response = httpx.get(self.api_url, params=params, timeout=10.0)
            if response.status_code != 200:
                print(f"GDELT Error: {response.status_code}")
                return []
            
            data = response.json()
            articles = data.get("articles", [])
            
            raw_docs = []
            for art in articles:
                raw_docs.append({
                    "id": art.get("url"), # Use URL as ID
                    "headline": art.get("title", "Untitled"),
                    "body": art.get("seendate", ""), # GDELT Artlist doesn't have full body
                    "url": art.get("url"),
                    "date": art.get("seendate", datetime.utcnow().isoformat()),
                    "socialimage": art.get("socialimage", ""),
                    "source_name": art.get("sourcecountry", "Global")
                })
            return raw_docs
        except Exception as e:
            print(f"GDELT Fetch Failed: {e}")
            return []
