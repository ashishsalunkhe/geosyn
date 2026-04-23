from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from app.models.domain import Document, EventCluster
from app.services.embedding_service import embedding_service
from app.services.event_service_v2 import EventServiceV2
import numpy as np

from app.pipelines.normalization import NormalizationPipeline
from app.core.metrics import clustering_runs_total

class ClusteringService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = NormalizationPipeline()
        self.time_window = timedelta(hours=48)
        self.event_service_v2 = EventServiceV2(db)

    def run_clustering(self) -> List[EventCluster]:
        """
        Processes unclustered documents and groups them into events.
        """
        # 1. Get all documents without a cluster
        unclustered_docs = self.db.query(Document).filter(Document.event_cluster_id == None).all()
        
        for doc in unclustered_docs:
            raw_themes = self.pipeline.extract_entities(doc.content)
            if not raw_themes:
                continue
            
            # extract_entities returns a list of dicts: [{"name": "...", "type": "..."}]
            themes = [t["name"].lower() for t in raw_themes]

            # 2. Look for existing clusters within the time window and shared themes
            best_cluster = self._find_best_cluster(doc, themes)
            
            if best_cluster:
                doc.event_cluster_id = best_cluster.id
                self.event_service_v2.sync_document_to_cluster_event(doc, best_cluster)
            else:
                # 3. Create a new cluster if no match found
                new_cluster = self._create_cluster(doc, themes)
                doc.event_cluster_id = new_cluster.id
                self.event_service_v2.sync_document_to_cluster_event(doc, new_cluster)

        self.db.commit()
        clustering_runs_total.inc()
        return self.db.query(EventCluster).all()



    def _find_best_cluster(self, doc: Document, themes: List[str]) -> Optional[EventCluster]:
        """
        Finds the most computationally relevant existing cluster using local Semantic Embeddings.
        Criteria: Time window + Semantic Similarity over 0.65 (threshold).
        """
        start_time = doc.published_at - self.time_window
        end_time = doc.published_at + self.time_window
        
        # Candidate clusters in the time window
        candidates = self.db.query(EventCluster).filter(
            EventCluster.created_at.between(start_time, end_time)
        ).all()
        
        if not candidates:
            return None
            
        # 1. Target representation: Title + SNIPPET + Themes
        target_str = f"{doc.title} {doc.content[:300]} {' '.join(themes)}".lower()
        target_embedding = embedding_service.embed_text(target_str)
        
        # 2. Build Cluster representations
        best_candidate = None
        max_similarity = 0
        
        for cluster in candidates:
            # We use the title and summary for semantic matching
            cluster_str = f"{cluster.title} {cluster.summary or ''}".lower()
            cluster_embedding = embedding_service.embed_text(cluster_str)
            
            similarity = embedding_service.compute_similarity(target_embedding, cluster_embedding)
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_candidate = cluster

        # 3. Threshold check (Semantic similarity is usually higher than TF-IDF)
        # 0.65 is a standard 'high confidence' match for miniLM models
        if max_similarity > 0.65:
            return best_candidate
            
        return None

    def _create_cluster(self, doc: Document, themes: List[str]) -> EventCluster:
        """
        Creates a new EventCluster using the document as the seed.
        """
        # Simple naming logic: Core theme + random snippet
        primary_theme = themes[0].capitalize() if themes else "Unknown"
        title = f"{primary_theme} Event: {doc.title[:50]}..."
        
        new_cluster = EventCluster(
            title=title,
            description=f"Generated cluster based on theme: {primary_theme}",
            created_at=doc.published_at,
            summary=doc.content[:200]
        )
        
        self.db.add(new_cluster)
        self.db.commit()
        self.db.refresh(new_cluster)
        return new_cluster
