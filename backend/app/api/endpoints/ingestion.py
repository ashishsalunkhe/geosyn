from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.services.ingestion_service import IngestionService
from app.services.exposure_import_service import ExposureImportService
from app.ingestion.gdelt_provider import GDELTProvider
from app.ingestion.rss_provider import RSSProvider
from app.ingestion.youtube_provider import YouTubeProvider
from app.workers.tasks import run_news_ingestion, run_compliance_ingestion

router = APIRouter()

class YouTubeIngestRequest(BaseModel):
    url: str

@router.post("/trigger")
def trigger_ingestion(enqueue: bool = False, db: Session = Depends(get_db)):
    """
    Manually trigger document ingestion from live GDELT and RSS sources.
    """
    if enqueue:
        task = run_news_ingestion.delay(True)
        return {"status": "queued", "task_id": task.id, "task_name": "run_news_ingestion"}

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


@router.post("/compliance")
async def ingest_compliance(
    db: Session = Depends(get_db),
    query: str = "",
    enqueue: bool = False,
):
    """
    Ingest compliance and sanctions-style official feed signals.
    """
    if enqueue:
        task = run_compliance_ingestion.delay(query)
        return {"status": "queued", "task_id": task.id, "task_name": "run_compliance_ingestion", "query": query}

    service = IngestionService(db)
    docs = await service.ingest_compliance_signals(query=query)
    return {
        "status": "success",
        "doc_count": len(docs),
        "query": query,
    }


@router.post("/exposure/csv")
async def import_exposure_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    """
    Import customer exposure links from a CSV file.
    Required columns:
    source_object_type, source_object_id, relationship_type, target_entity_name
    Supported source_object_type values:
    supplier, facility, port, route, commodity, customer_asset
    """
    raw = await file.read()
    try:
        csv_text = raw.decode("utf-8")
        service = ExposureImportService(db)
        result = service.import_csv(csv_text, current_customer.id)
        return {"status": "success", "customer_id": current_customer.id, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/exposure/csv/validate")
async def validate_exposure_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    """
    Validate an exposure CSV without writing it to the database.
    Returns row counts, errors, warnings, and a preview sample.
    """
    raw = await file.read()
    try:
        csv_text = raw.decode("utf-8")
        service = ExposureImportService(db)
        result = service.validate_csv(csv_text, current_customer.id)
        return {"status": "success", "customer_id": current_customer.id, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
