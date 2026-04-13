from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.services.ingestion_service import IngestionService
from app.ingestion.gdelt_provider import GDELTProvider
from app.ingestion.rss_provider import RSSProvider
from app.ingestion.youtube_provider import YouTubeProvider

router = APIRouter()

class YouTubeIngestRequest(BaseModel):
    url: str

@router.post("/trigger")
def trigger_ingestion(db: Session = Depends(get_db)):
    """
    Manually trigger document ingestion from live GDELT and RSS sources.
    """
    service = IngestionService(db)
    
    # 1. Fetch from GDELT
    gdelt = GDELTProvider()
    gdelt_docs = service.run_ingestion(gdelt)
    
    # 2. Fetch from RSS
    rss = RSSProvider()
    rss_docs = service.run_ingestion(rss)
    
    return {
        "status": "success",
        "sources": [gdelt.provider_name, rss.provider_name],
        "total_ingested": len(gdelt_docs) + len(rss_docs)
    }

@router.post("/youtube")
def ingest_youtube(request: YouTubeIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a YouTube video and extract data.
    """
    service = IngestionService(db)
    provider = YouTubeProvider(request.url)
    docs = service.run_ingestion(provider)
    
    return {
        "status": "success",
        "doc_count": len(docs)
    }
