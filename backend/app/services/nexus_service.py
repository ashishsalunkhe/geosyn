from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.models.domain import CausalNode, CausalEdge, EventCluster, MarketSeries, Entity, Document
import re
from app.services.causality_engine import causality_engine
from app.ingestion.fred_provider import fred_provider
from app.ingestion.imf_provider import IMFProvider
from app.ingestion.world_bank_provider import WorldBankProvider
from app.services.gpr_index_service import GPRIndexService

class NexusService:
    def __init__(self, db: Session):
        self.db = db

    def sync_knowledge_graph(self):
        """
        Synchronizes the knowledge graph by mapping events, assets, and entities to nodes
        and discovering causal edges between them.
        """
        # 1. Map Events to Nodes
        events = self.db.query(EventCluster).all()
        for ev in events:
            self._get_or_create_node("event", ev.id, ev.title)

        # 2. Map Assets to Nodes
        assets = self.db.query(MarketSeries).all()
        for asset in assets:
            self._get_or_create_node("asset", asset.id, asset.ticker)

        # 3. Map Macro Indicators to Nodes (FRED, IMF, World Bank)
        # FRED Signals (USD Focused)
        for series_id, name in fred_provider.SERIES_MAP.items():
            # Use hash-based IDs to avoid collision with incremental DB IDs
            self._get_or_create_node("entity", -abs(hash(series_id) % 10000), f"Macro: {name}")

        # IMF Signals (Global Focused)
        imf_indicators = IMFProvider.INDICATORS
        for code, name in imf_indicators.items():
            self._get_or_create_node("entity", -abs(hash(code) % 20000), f"IMF: {name}")

        # World Bank Signals (Trade/Energy Focused)
        wb_indicators = WorldBankProvider.INDICATORS
        for code, name in wb_indicators.items():
            self._get_or_create_node("entity", -abs(hash(code) % 30000), f"WB: {name}")

        # 4. Discover Relationships (Causal Edges)
        self._extract_causal_relationships()
        
        self.db.commit()

    def _get_or_create_node(self, node_type: str, entity_id: int, name: str) -> CausalNode:
        node = self.db.query(CausalNode).filter(
            CausalNode.entity_type == node_type,
            CausalNode.entity_id == entity_id
        ).first()
        
        if not node:
            node = CausalNode(
                entity_type=node_type,
                entity_id=entity_id,
                name=name,
                importance=1.0
            )
            self.db.add(node)
            self.db.flush()
        return node

    def _extract_causal_relationships(self):
        """
        Discovers edges between nodes using two strategies:

        1. Event → Asset edges: if a document contains plain-language keywords
           for a market asset (e.g. 'crude oil' → CL=F), create a weighted edge.
           This replaces the old literal ticker matching which never fired on
           real news articles.

        2. Event → Event edges: if two EventClusters share 2+ theme words,
           create an edge representing thematic co-occurrence (may indicate
           a shared driver or escalation path).
        """
        # ------------------------------------------------------------------
        # Strategy 1: Event → Asset via plain-language keyword matching
        # ------------------------------------------------------------------
        KEYWORD_TO_TICKER = {
            "oil": "CL=F", "crude": "CL=F", "petroleum": "CL=F",
            "brent": "CL=F", "opec": "CL=F", "barrel": "CL=F",
            "gold": "GC=F", "precious metal": "GC=F", "bullion": "GC=F",
            "s&p": "^GSPC", "wall street": "^GSPC", "nasdaq": "^GSPC",
            "dow jones": "^GSPC", "us market": "^GSPC", "american stock": "^GSPC",
            "sensex": "^BSESN", "bse": "^BSESN", "bombay": "^BSESN",
            "nifty": "^NSEI", "nse": "^NSEI", "india market": "^NSEI",
        }

        CAUSAL_MARKERS = {
            "negative": ["plunge", "blockade", "sanction", "drop", "crash", "war",
                         "conflict", "threaten", "damage", "collapse", "attack",
                         "missile", "invasion", "embargo", "tariff", "restrict"],
            "positive":  ["soar", "surge", "resolution", "deal", "treaty", "growth",
                          "stabilize", "increase", "agreement", "rally", "boost",
                          "recovery", "cooperation", "ease", "lift"]
        }

        # Process ALL documents linked to an event cluster (no recency filter —
        # the old 24h filter caused zero documents to qualify on most runs)
        docs = self.db.query(Document).filter(Document.event_cluster_id.isnot(None)).all()

        for doc in docs:
            if not doc.content:
                continue
            event_node = self._get_or_create_node("event", doc.event_cluster_id,
                                                   doc.event_cluster.title if doc.event_cluster else f"Event {doc.event_cluster_id}")
            content_lower = doc.content.lower()

            # Calculate sentiment weight from causal markers
            weight = 0.0
            for word in CAUSAL_MARKERS["negative"]:
                if word in content_lower:
                    weight -= 0.25
            for word in CAUSAL_MARKERS["positive"]:
                if word in content_lower:
                    weight += 0.25
            weight = max(-1.0, min(1.0, weight))

            # Match keywords to tickers
            matched_tickers = set()
            for keyword, ticker in KEYWORD_TO_TICKER.items():
                if keyword in content_lower:
                    matched_tickers.add(ticker)

            for ticker in matched_tickers:
                asset_series = self.db.query(MarketSeries).filter(
                    MarketSeries.ticker == ticker
                ).first()
                if not asset_series:
                    continue
                asset_node = self._get_or_create_node("asset", asset_series.id, ticker)
                
                # --- Enterprise Addition: Validate with Granger Causality ---
                # We fetch a 14-day history for the ticker returns and the event news volume
                # If the test is significant, we boost the weight and add 'evidence' text.
                evidence_text = f"Keyword match: '{doc.title[:40]}...'"
                confidence = 0.5 # Baseline
                
                # (Conceptual: In a full run, we'd pass real time-series arrays here)
                # For now, we store the metadata for the frontend to render.
                
                self._create_edge(event_node.id, asset_node.id, "impacts", weight, evidence_text)

        # ------------------------------------------------------------------
        # Strategy 2: Event → Event co-occurrence edges via shared themes
        # ------------------------------------------------------------------
        events = self.db.query(EventCluster).all()

        # Build a simple keyword set per event from its title + description
        def keywords(ev: EventCluster):
            text = ((ev.title or "") + " " + (ev.description or "")).lower()
            # Strip stopwords naively — split on whitespace and remove short tokens
            stop = {"the", "a", "an", "in", "of", "and", "or", "to", "for", "is",
                    "was", "at", "by", "on", "with", "from", "that", "this", "it",
                    "as", "be", "are", "has", "have", "had", "been", "will", "not"}
            return {w for w in text.split() if len(w) > 3 and w not in stop}

        event_keywords = [(ev, keywords(ev)) for ev in events]

        for i, (ev_a, kw_a) in enumerate(event_keywords):
            for ev_b, kw_b in event_keywords[i+1:]:
                shared = kw_a & kw_b
                if len(shared) >= 2:  # At least 2 shared meaningful words
                    node_a = self._get_or_create_node("event", ev_a.id, ev_a.title)
                    node_b = self._get_or_create_node("event", ev_b.id, ev_b.title)
                    # Weight proportional to overlap depth
                    overlap_score = min(1.0, len(shared) * 0.15)
                    self._create_edge(node_a.id, node_b.id, "co-occurs", overlap_score, f"Shared topics: {', '.join(list(shared)[:3])}")



    def _create_edge(self, source_id: int, target_id: int, rel_type: str, weight: float, evidence: str):
        # Check if edge already exists for this pair today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        existing = self.db.query(CausalEdge).filter(
            CausalEdge.source_node_id == source_id,
            CausalEdge.target_node_id == target_id,
            CausalEdge.created_at >= today_start
        ).first()

        if existing:
            # Update weight (averaging or taking strongest)
            if abs(weight) > abs(existing.weight):
                existing.weight = weight
        else:
            edge = CausalEdge(
                source_node_id=source_id,
                target_node_id=target_id,
                relation_type=rel_type,
                weight=weight,
                evidence=evidence
            )
            self.db.add(edge)

    def get_graph_data(self) -> Dict[str, Any]:
        """Formatted for the SVG force-directed graph.
        
        Node importance is computed dynamically from degree centrality
        (number of edges connected to that node). This makes highly-connected
        nodes render larger, giving a visual sense of influence.
        """
        nodes = self.db.query(CausalNode).all()
        edges = self.db.query(CausalEdge).all()

        # Build degree map: node_id → edge count
        degree: Dict[int, int] = {n.id: 0 for n in nodes}
        for e in edges:
            degree[e.source_node_id] = degree.get(e.source_node_id, 0) + 1
            degree[e.target_node_id] = degree.get(e.target_node_id, 0) + 1

        max_degree = max(degree.values(), default=1) or 1

        return {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.entity_type,
                    # Normalised importance: 0.2 (isolated) → 1.0 (most connected)
                    "importance": 0.2 + 0.8 * (degree[n.id] / max_degree),
                    "val": (0.2 + 0.8 * (degree[n.id] / max_degree)) * 5,
                    "meta": n.node_meta
                } for n in nodes
            ],
            "links": [
                {
                    "source": e.source_node_id,
                    "target": e.target_node_id,
                    "type": e.relation_type,
                    "weight": e.weight,
                    "color": "#10b981" if e.weight > 0 else "#f43f5e" if e.weight < 0 else "#a1a1aa"
                } for e in edges
            ]
        }
