from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.services.watchlist_service_v2 import WatchlistServiceV2

router = APIRouter()


class WatchlistCreateRequest(BaseModel):
    name: str
    watchlist_type: str | None = None
    is_default: bool = False


class WatchlistItemCreateRequest(BaseModel):
    canonical_name: str
    entity_type: str = "company"
    item_type: str = "entity"
    criticality_score: float | None = None


@router.get("/", response_model=list[dict])
def list_watchlists(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = WatchlistServiceV2(db)
    return [service.serialize_watchlist(row) for row in service.list_watchlists(current_customer.id)]


@router.post("/", response_model=dict)
def create_watchlist(
    payload: WatchlistCreateRequest,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = WatchlistServiceV2(db)
    watchlist = service.create_watchlist(
        current_customer,
        name=payload.name,
        watchlist_type=payload.watchlist_type,
        is_default=payload.is_default,
    )
    return service.serialize_watchlist(watchlist)


@router.post("/{watchlist_id}/items", response_model=dict)
def add_watchlist_item(
    watchlist_id: str,
    payload: WatchlistItemCreateRequest,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = WatchlistServiceV2(db)
    try:
        item = service.add_item(
            watchlist_id,
            current_customer.id,
            canonical_name=payload.canonical_name,
            entity_type=payload.entity_type,
            item_type=payload.item_type,
            criticality_score=payload.criticality_score,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    watchlist = service.get_watchlist(watchlist_id, current_customer.id)
    return {
        "item": {
            "id": item.id,
            "entity_id": item.entity_id,
            "canonical_name": item.entity.canonical_name if item.entity else None,
            "display_name": item.entity.display_name if item.entity else None,
            "entity_type": item.entity.entity_type if item.entity else None,
            "item_type": item.item_type,
            "criticality_score": item.criticality_score,
        },
        "watchlist": service.serialize_watchlist(watchlist) if watchlist else None,
    }


@router.delete("/items/{item_id}", response_model=dict)
def delete_watchlist_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = WatchlistServiceV2(db)
    try:
        service.remove_item(item_id, current_customer.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "success", "item_id": item_id}
