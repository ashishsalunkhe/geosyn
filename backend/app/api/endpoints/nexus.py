from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.session import get_db
from app.services.nexus_service import NexusService
from app.workers.tasks import run_nexus_sync

router = APIRouter()

@router.get("/graph", response_model=Dict[str, Any])
def get_causal_graph(db: Session = Depends(get_db)):
    """
    Returns the Knowledge Graph formatted for force-directed visualization.
    """
    service = NexusService(db)
    return service.get_graph_data()

@router.post("/sync")
def sync_nexus(enqueue: bool = False, db: Session = Depends(get_db)):
    """
    Manually triggers the relationship extraction and graph synchronization.
    """
    if enqueue:
        task = run_nexus_sync.delay()
        return {"status": "queued", "task_id": task.id, "task_name": "run_nexus_sync"}

    service = NexusService(db)
    service.sync_knowledge_graph()
    return {"status": "success", "message": "Nexus Knowledge Graph synchronized"}
