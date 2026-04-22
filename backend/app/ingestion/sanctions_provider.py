from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import feedparser

from app.ingestion.base import BaseProvider


class SanctionsProvider(BaseProvider):
    """
    Lightweight compliance-oriented ingestion provider based on official sanctions
    and export-control style release feeds.
    """

    FEEDS = [
        ("OFAC Recent Actions", "https://ofac.treasury.gov/recent-actions/feed"),
        ("BIS News", "https://www.bis.doc.gov/index.php/all-articles?format=feed&type=rss"),
    ]

    @property
    def provider_name(self) -> str:
        return "Compliance Sanctions Monitor"

    @property
    def source_type(self) -> str:
        return "compliance"

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []
        query_text = (query or "").lower().strip()

        for publisher, feed_url in self.FEEDS:
            try:
                parsed = feedparser.parse(feed_url)
                for entry in parsed.entries[:20]:
                    title = getattr(entry, "title", "Untitled Compliance Update")
                    summary = getattr(entry, "summary", "")
                    content = summary or getattr(entry, "description", "")
                    link = getattr(entry, "link", "")
                    combined = f"{title} {content}".lower()
                    if query_text and query_text not in combined:
                        continue
                    published = self._parse_published(entry)
                    documents.append(
                        {
                            "id": link or f"{publisher}-{title}",
                            "title": title,
                            "content": content,
                            "url": link,
                            "source": publisher,
                            "seendate": published,
                            "themes": ["COMPLIANCE", "SANCTIONS", "TRADE"],
                            "tone": -2.5 if "sanction" in combined or "restriction" in combined else -0.5,
                        }
                    )
            except Exception as exc:  # noqa: BLE001
                print(f"SanctionsProvider feed error on {feed_url}: {exc}")

        documents.sort(key=lambda item: item["seendate"], reverse=True)
        return documents

    @staticmethod
    def _parse_published(entry: Any) -> str:
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if parsed:
            return datetime(*parsed[:6]).isoformat() + "Z"
        return datetime.utcnow().isoformat() + "Z"
