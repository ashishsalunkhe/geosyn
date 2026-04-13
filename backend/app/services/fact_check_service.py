from sqlalchemy.orm import Session
from typing import List
from app.models.domain import Claim, Document, EventCluster
from app.pipelines.normalization import NormalizationPipeline

class FactCheckService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = NormalizationPipeline()

    def verify_claim(self, claim_id: int) -> Claim:
        """
        Cross-references a claim against documents in its event cluster.
        """
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim or not claim.event_cluster_id:
            return claim

        # 1. Get other evidence in the same cluster
        evidence_pool = self.db.query(Document).filter(
            Document.event_cluster_id == claim.event_cluster_id,
            Document.id != claim.document_id
        ).all()

        if not evidence_pool:
            claim.verdict = "unverified"
            self.db.commit()
            return claim

        # 2. Extract keywords from claim for comparison
        # (Simplified: looking for thematic overlap)
        claim_themes = self.pipeline.extract_entities(claim.text)
        
        supporting_count = 0
        contradicting_count = 0
        
        for doc in evidence_pool:
            doc_themes = self.pipeline.extract_entities(doc.content)
            
            # Intersection of themes
            overlap = set(claim_themes).intersection(set(doc_themes))
            
            if overlap:
                # Basic heuristic: if they share themes, we check for 'contradiction' markers
                # e.g., if one says 'escalation' and other doesn't
                content_lower = doc.content.lower()
                if "false" in content_lower or "unlikely" in content_lower or "deny" in content_lower:
                    contradicting_count += 1
                else:
                    supporting_count += 1

        # 3. Determine Verdict
        if contradicting_count > 0 and supporting_count > 0:
            claim.verdict = "mixed"
        elif contradicting_count > supporting_count:
            claim.verdict = "contradicted"
        elif supporting_count >= 2: # Require at least 2 independent sources
            claim.verdict = "supported"
        elif supporting_count == 1:
            claim.verdict = "unverified" # Still need more evidence
        else:
            claim.verdict = "unverified"

        self.db.commit()
        return claim

    def verify_all_claims_in_event(self, event_id: int) -> List[Claim]:
        claims = self.db.query(Claim).filter(Claim.event_cluster_id == event_id).all()
        for c in claims:
            self.verify_claim(c.id)
        return claims
