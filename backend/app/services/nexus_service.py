from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.models.domain import CausalNode, CausalEdge, EventCluster, MarketSeries, Entity, Document
import re

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

        # 3. Discover Relationships (Causal Edges)
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
        Heuristic: If an Event and an Asset/Entity are mentioned in the same document
        and certain 'causal keywords' are present, we create a weighted edge.
        """
        # Causal markers for relationship direction/intensity
        CAUSAL_MARKERS = {
            "negative": ["plunge", "blockade", "sanction", "drop", "crash", "war", "conflict", "threaten", "damage"],
            "positive": ["soar", "surge", "resolution", "deal", "treaty", "growth", "stabilize", "increase"]
        }

        # Processes all documents from the last 24 hours
        recent_docs = self.db.query(Document).filter(
            Document.normalized_at > datetime.utcnow() - timedelta(hours=24)
        ).all()

        for doc in recent_docs:
            if not doc.event_cluster_id: continue
            
            event_node = self._get_or_create_node("event", doc.event_cluster_id, doc.event_cluster.title)
            
            # Look for Asset mentions in the same document
            from app.core.tickers import ALL_TRACKED_TICKERS
            content_lower = doc.content.lower()
            
            for ticker in ALL_TRACKED_TICKERS:
                if f"${ticker.lower()}" in content_lower or f" {ticker.lower()} " in content_lower:
                    asset_series = self.db.query(MarketSeries).filter(MarketSeries.ticker == ticker).first()
                    if not asset_series: continue
                    
                    asset_node = self._get_or_create_node("asset", asset_series.id, ticker)
                    
                    # Sentiment weight calculation
                    weight = 0.0
                    for word in CAUSAL_MARKERS["negative"]:
                        if word in content_lower: weight -= 0.3
                    for word in CAUSAL_MARKERS["positive"]:
                        if word in content_lower: weight += 0.3
                    
                    weight = max(-1.0, min(1.0, weight)) # Clamp

                    # Create Edge
                    self._create_edge(event_node.id, asset_node.id, "impacts", weight, doc.title)

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
        """Formatted for react-force-graph"""
        nodes = self.db.query(CausalNode).all()
        edges = self.db.query(CausalEdge).all()
        
        return {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.entity_type,
                    "importance": n.importance,
                    "val": n.importance * 5
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
