from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.v2 import CustomerV2, WatchlistV2


class CustomerServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def get_by_slug(self, slug: str) -> Optional[CustomerV2]:
        return self.db.query(CustomerV2).filter(CustomerV2.slug == slug).first()

    def get_or_create_demo_customer(self) -> CustomerV2:
        customer = self.get_by_slug("demo")
        if customer:
            return customer

        now = datetime.utcnow()
        customer = CustomerV2(
            name="GeoSyn Demo",
            slug="demo",
            industry="general",
            primary_region="global",
            created_at=now,
            updated_at=now,
        )
        self.db.add(customer)
        self.db.flush()

        default_watchlists = [
            ("Core Events", "events", True),
            ("Critical Suppliers", "suppliers", False),
            ("Strategic Geographies", "geographies", False),
            ("Key Commodities", "commodities", False),
        ]
        for name, watchlist_type, is_default in default_watchlists:
            self.db.add(
                WatchlistV2(
                    customer_id=customer.id,
                    name=name,
                    watchlist_type=watchlist_type,
                    is_default=is_default,
                    created_at=now,
                )
            )

        self.db.commit()
        self.db.refresh(customer)
        return customer
