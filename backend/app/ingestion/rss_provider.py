import feedparser
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.ingestion.base import BaseProvider

class RSSProvider(BaseProvider):
    """
    Integrates with robust, primary-source XML RSS feeds to generate high-volume,
    real-time macroeconomic and geopolitical data without IP bans or rate limits.
    """
    
    # Highly reputable global feeds covering markets, finance, and geopolitics
    FEEDS = [
        "https://feeds.a.dj.com/rss/RSSWorldNews.xml", # WSJ World
        "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml", # WSJ Business
        "http://feeds.bbci.co.uk/news/world/rss.xml", # BBC World
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # CNBC Finance
    ]

    @property
    def provider_name(self) -> str:
        return "Global RSS Aggregator"

    @property
    def source_type(self) -> str:
        return "rss"

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Polls all RSS feeds. If a query is provided, performs heuristic filtering
        on titles and descriptions. Otherwise returns the firehose.
        """
        all_articles = []
        
        for feed_url in self.FEEDS:
            try:
                parsed = feedparser.parse(feed_url)
                
                # Identify publisher from the feed's base metadata
                publisher = "GLOBAL MONITOR"
                if "title" in parsed.feed:
                    publisher = parsed.feed.title.split("-")[0].strip().upper()
                
                for entry in parsed.entries[:20]: # Extract top 20 recent items per feed
                    title = getattr(entry, "title", "Untitled News")
                    description = getattr(entry, "summary", "")
                    link = getattr(entry, "link", "")
                    
                    # Filtering logic if query provided
                    if query:
                        content_str = (title + " " + description).lower()
                        # Allow boolean-like OR extraction
                        query_terms = query.lower().replace("or", " ").replace("and", " ").split()
                        matches = any(term in content_str for term in query_terms if term)
                        if not matches:
                            continue
                    
                    # Parse Time (RSS generally uses structured time_parsed)
                    published = datetime.utcnow().isoformat() + "Z"
                    raw_time = entry.get("published_parsed")
                    if raw_time:
                        published = datetime.fromtimestamp(time.mktime(raw_time)).isoformat() + "Z"
                    
                    # Compute crude heuristic sentiment for Live Feed rendering
                    # We will use the ML NLP layer later, but basic tagging helps the UI
                    content_lower = (title + " " + description).lower()
                    tone = 0.0
                    for negative in ["drop", "plunge", "crisis", "conflict", "war", "alert", "shock"]:
                        if negative in content_lower: tone -= 3.5
                    for positive in ["deal", "soar", "gain", "growth", "stabilize", "rebound"]:
                        if positive in content_lower: tone += 3.5
                        
                    all_articles.append({
                        "id": link, # Unique Ident by URL
                        "title": title,
                        "content": description,
                        "url": link,
                        "source": publisher,
                        "seendate": published, # Same structure as GDELT for frontend parity
                        "tone": tone,
                        "themes": ["MACRO", "GEO"]
                    })
            except Exception as e:
                print(f"RSS Fetch Error on {feed_url}: {e}")
                
        # Sort by most recent
        all_articles.sort(key=lambda x: x["seendate"], reverse=True)
        return all_articles
