import re
from sqlalchemy.orm import Session
from typing import List
from app.models.domain import Document, Claim

class ClaimService:
    def __init__(self, db: Session):
        self.db = db

    def extract_claims_from_document(self, doc_id: int) -> List[Claim]:
        """
        Extracts claims from a document based on simple triggers (e.g., 'CLAIM:').
        """
        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return []

        # Simple regex to find text following 'CLAIM:'
        # In production, this would be an LLM-based extraction
        found_claims = re.findall(r"CLAIM:\s*(.*?)(?=\.|$)", doc.content, re.IGNORECASE)
        
        claims = []
        for text in found_claims:
            # Check if this claim already exists for this document
            existing = self.db.query(Claim).filter(
                Claim.document_id == doc.id,
                Claim.text == text.strip()
            ).first()
            
            if existing:
                continue

            new_claim = Claim(
                document_id=doc.id,
                event_cluster_id=doc.event_cluster_id,
                text=text.strip(),
                verdict="unverified",
                confidence_score=0.5
            )
            self.db.add(new_claim)
            claims.append(new_claim)
        
        self.db.commit()
        return claims
