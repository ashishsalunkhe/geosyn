from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.clustering_service import ClusteringService

router = APIRouter()

@router.post("/trigger")
def trigger_clustering(db: Session = Depends(get_db)):
    """
    Manually trigger document clustering into events.
    """
    service = ClusteringService(db)
    event_clusters = service.run_clustering()
    
    return {
        "status": "success",
        "cluster_count": len(event_clusters)
    }
