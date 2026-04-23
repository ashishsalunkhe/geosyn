from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import get_db
from app.services.market_service import MarketService
from app.workers.tasks import run_market_sync

router = APIRouter()

@router.post("/sync")
async def sync_markets(enqueue: bool = False, db: Session = Depends(get_db)):
    """
    Sync market data into the database asynchronously.
    """
    try:
        if enqueue:
            task = run_market_sync.delay()
            return {"status": "queued", "task_id": task.id, "task_name": "run_market_sync"}
        service = MarketService(db)
        await service.sync_market_data()
        return {"status": "success", "message": "Market data synced"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation/{ticker}")
def get_market_correlation(ticker: str, db: Session = Depends(get_db)):
    """
    Get market time series correlated with geopolitical event shocks.
    """
    service = MarketService(db)
    data = service.get_market_narrative_shocks(ticker)
    return data
