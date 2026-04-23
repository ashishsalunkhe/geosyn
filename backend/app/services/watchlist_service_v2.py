from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.v2 import CustomerV2, EntityV2, WatchlistItemV2, WatchlistV2


class WatchlistServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def list_watchlists(self, customer_id: str) -> List[WatchlistV2]:
        return (
            self.db.query(WatchlistV2)
            .filter(WatchlistV2.customer_id == customer_id)
            .order_by(WatchlistV2.is_default.desc(), WatchlistV2.created_at.asc())
            .all()
        )

    def get_watchlist(self, watchlist_id: str, customer_id: str) -> Optional[WatchlistV2]:
        return (
            self.db.query(WatchlistV2)
            .filter(WatchlistV2.id == watchlist_id, WatchlistV2.customer_id == customer_id)
            .first()
        )

    def create_watchlist(
        self,
        customer: CustomerV2,
        *,
        name: str,
        watchlist_type: Optional[str] = None,
        is_default: bool = False,
    ) -> WatchlistV2:
        watchlist = WatchlistV2(
            customer_id=customer.id,
            name=name.strip(),
            watchlist_type=(watchlist_type or "").strip() or None,
            is_default=is_default,
            created_at=datetime.utcnow(),
        )
        self.db.add(watchlist)
        self.db.commit()
        self.db.refresh(watchlist)
        return watchlist

    def add_item(
        self,
        watchlist_id: str,
        customer_id: str,
        *,
        canonical_name: str,
        entity_type: str,
        item_type: str,
        criticality_score: float | None = None,
    ) -> WatchlistItemV2:
        watchlist = self.get_watchlist(watchlist_id, customer_id)
        if not watchlist:
            raise ValueError("Watchlist not found")

        entity = self._get_or_create_entity(canonical_name.strip(), entity_type.strip().lower() or "company")
        existing = (
            self.db.query(WatchlistItemV2)
            .filter(
                WatchlistItemV2.watchlist_id == watchlist.id,
                WatchlistItemV2.entity_id == entity.id,
                WatchlistItemV2.item_type == item_type,
            )
            .first()
        )
        if existing:
            return existing

        item = WatchlistItemV2(
            watchlist_id=watchlist.id,
            entity_id=entity.id,
            item_type=item_type.strip().lower() or "entity",
            criticality_score=criticality_score,
            created_at=datetime.utcnow(),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_item(self, item_id: str, customer_id: str) -> None:
        item = (
            self.db.query(WatchlistItemV2)
            .join(WatchlistV2, WatchlistV2.id == WatchlistItemV2.watchlist_id)
            .filter(WatchlistItemV2.id == item_id, WatchlistV2.customer_id == customer_id)
            .first()
        )
        if not item:
            raise ValueError("Watchlist item not found")
        self.db.delete(item)
        self.db.commit()

    def serialize_watchlist(self, watchlist: WatchlistV2) -> Dict[str, Any]:
        return {
            "id": watchlist.id,
            "name": watchlist.name,
            "watchlist_type": watchlist.watchlist_type,
            "is_default": watchlist.is_default,
            "item_count": len(watchlist.items),
            "items": [
                {
                    "id": item.id,
                    "entity_id": item.entity_id,
                    "canonical_name": item.entity.canonical_name if item.entity else None,
                    "display_name": item.entity.display_name if item.entity else None,
                    "entity_type": item.entity.entity_type if item.entity else None,
                    "item_type": item.item_type,
                    "criticality_score": item.criticality_score,
                }
                for item in watchlist.items
            ],
        }

    def _get_or_create_entity(self, canonical_name: str, entity_type: str) -> EntityV2:
        existing = (
            self.db.query(EntityV2)
            .filter(EntityV2.canonical_name == canonical_name, EntityV2.entity_type == entity_type)
            .first()
        )
        if existing:
            return existing

        entity = EntityV2(
            canonical_name=canonical_name,
            display_name=canonical_name,
            entity_type=entity_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(entity)
        self.db.flush()
        return entity
