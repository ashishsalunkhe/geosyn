import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal  # noqa: E402
from app.models.v2 import CustomerV2, WatchlistV2  # noqa: E402


def seed() -> None:
    db = SessionLocal()
    try:
        customer = db.query(CustomerV2).filter(CustomerV2.slug == "demo").first()
        if not customer:
            customer = CustomerV2(
                name="GeoSyn Demo",
                slug="demo",
                industry="general",
                primary_region="global",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(customer)
            db.flush()

        existing_types = {
            row.watchlist_type
            for row in db.query(WatchlistV2).filter(WatchlistV2.customer_id == customer.id).all()
        }
        default_watchlists = [
            ("Core Events", "events", True),
            ("Critical Suppliers", "suppliers", False),
            ("Strategic Geographies", "geographies", False),
            ("Key Commodities", "commodities", False),
        ]
        for name, watchlist_type, is_default in default_watchlists:
            if watchlist_type in existing_types:
                continue
            db.add(
                WatchlistV2(
                    customer_id=customer.id,
                    name=name,
                    watchlist_type=watchlist_type,
                    is_default=is_default,
                    created_at=datetime.utcnow(),
                )
            )

        db.commit()
        print("Seed complete. Demo customer and default watchlists are ready.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
