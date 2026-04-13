from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import domain as schemas
# from app.services import document_service # To be implemented

router = APIRouter()

@router.get("/", response_model=List[schemas.Document])
def read_documents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    from app.models.domain import Document
    return db.query(Document).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=schemas.Document)
def read_document_by_id(
    id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get document by ID.
    """
    from app.models.domain import Document
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
