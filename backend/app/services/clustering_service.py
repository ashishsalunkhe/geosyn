from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from app.models.domain import Document, EventCluster
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.pipelines.normalization import NormalizationPipeline

class ClusteringService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = NormalizationPipeline()
        self.time_window = timedelta(hours=48)

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
            else:
                # 3. Create a new cluster if no match found
                new_cluster = self._create_cluster(doc, themes)
                doc.event_cluster_id = new_cluster.id
        
        self.db.commit()
        return self.db.query(EventCluster).all()



    def _find_best_cluster(self, doc: Document, themes: List[str]) -> Optional[EventCluster]:
        """
        Finds the most computationally relevant existing cluster using ML vectorization.
        Criteria: Time window + TF-IDF Cosine Similarity over 0.25 (threshold).
        """
        start_time = doc.published_at - self.time_window
        end_time = doc.published_at + self.time_window
        
        # Candidate clusters in the time window
        candidates = self.db.query(EventCluster).filter(
            EventCluster.created_at.between(start_time, end_time)
        ).all()
        
        if not candidates:
            return None
            
        # Target representation
        target_str = (doc.title + " " + doc.content + " " + " ".join(themes)).lower()
        
        # Build Corpus of Candidates
        corpus = []
        for cluster in candidates:
            corpus.append((cluster.title + " " + cluster.description + " " + (cluster.summary or "")).lower())
            
        # We append the target document to the end of the corpus structure to share vector space
        corpus.append(target_str)
        
        # Vectorize using Term-Frequency Inverse-Document-Frequency
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Compute Cosine Similarity between our target string (the last matrix row)
            # and all other preceding rows (the candidates)
            target_vector = tfidf_matrix[-1]
            candidate_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(target_vector, candidate_vectors)[0]
            
            # Identify max scoring mathematical match
            max_index = np.argmax(similarities)
            max_score = similarities[max_index]
            
            # Require a mathematical threshold match (> 15% similarity)
            if max_score > 0.15:
                return candidates[max_index]
            return None
        except Exception as e:
            print(f"ML Clustering computation error: {e}")
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
