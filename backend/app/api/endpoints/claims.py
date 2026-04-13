from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import get_db
from app.schemas import domain as schemas
from app.services.claim_service import ClaimService
from app.services.fact_check_service import FactCheckService

router = APIRouter()

@router.get("/", response_model=List[schemas.Claim])
def read_claims(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all claims.
    """
    from app.models.domain import Claim
    return db.query(Claim).offset(skip).limit(limit).all()

@router.post("/extract/{doc_id}")
def extract_claims(doc_id: int, db: Session = Depends(get_db)):
    """
    Trigger claim extraction for a specific document.
    """
    service = ClaimService(db)
    claims = service.extract_claims_from_document(doc_id)
    return {"status": "success", "claim_count": len(claims)}

@router.post("/verify/event/{event_id}")
def verify_event_claims(event_id: int, db: Session = Depends(get_db)):
    """
    Trigger fact-checking for all claims in an event cluster.
    """
    service = FactCheckService(db)
    claims = service.verify_all_claims_in_event(event_id)
    return {"status": "success", "verified_count": len(claims)}
