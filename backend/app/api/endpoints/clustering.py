from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.clustering_service import ClusteringService
from app.workers.tasks import run_clustering

router = APIRouter()

@router.post("/trigger")
def trigger_clustering(enqueue: bool = False, db: Session = Depends(get_db)):
    """
    Manually trigger document clustering into events.
    """
    if enqueue:
        task = run_clustering.delay()
        return {"status": "queued", "task_id": task.id, "task_name": "run_clustering"}

    service = ClusteringService(db)
    event_clusters = service.run_clustering()
    
    return {
        "status": "success",
        "cluster_count": len(event_clusters)
    }
