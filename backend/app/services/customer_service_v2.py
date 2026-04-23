from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.v2 import (
    AlertV2,
    CommodityV2,
    CustomerAssetV2,
    CustomerV2,
    EventV2,
    ExposureLinkV2,
    FacilityV2,
    PortV2,
    RouteV2,
    SupplierV2,
    WatchlistItemV2,
    WatchlistV2,
)


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

    def get_overview(self, customer: CustomerV2) -> dict:
        exposure_link_count = self.db.query(ExposureLinkV2).filter(ExposureLinkV2.customer_id == customer.id).count()
        supplier_count = self.db.query(SupplierV2).filter(SupplierV2.customer_id == customer.id).count()
        facility_count = self.db.query(FacilityV2).filter(FacilityV2.customer_id == customer.id).count()
        asset_count = self.db.query(CustomerAssetV2).filter(CustomerAssetV2.customer_id == customer.id).count()
        watchlist_count = self.db.query(WatchlistV2).filter(WatchlistV2.customer_id == customer.id).count()
        watchlist_item_count = (
            self.db.query(WatchlistItemV2)
            .join(WatchlistV2, WatchlistV2.id == WatchlistItemV2.watchlist_id)
            .filter(WatchlistV2.customer_id == customer.id)
            .count()
        )
        alert_count = self.db.query(AlertV2).filter(AlertV2.customer_id == customer.id).count()
        open_alert_count = (
            self.db.query(AlertV2)
            .filter(AlertV2.customer_id == customer.id, AlertV2.status.notin_(["dismissed", "mitigated"]))
            .count()
        )
        active_event_count = self.db.query(EventV2).filter(EventV2.status.in_(["active", "emerging"])).count()

        shared_object_counts = {
            "ports": self.db.query(PortV2).count(),
            "routes": self.db.query(RouteV2).count(),
            "commodities": self.db.query(CommodityV2).count(),
        }

        onboarding = {
            "has_customer_profile": True,
            "has_watchlists": watchlist_count > 0,
            "has_watchlist_items": watchlist_item_count > 0,
            "has_exposure_links": exposure_link_count > 0,
            "ready_for_exposure_alerting": exposure_link_count > 0,
        }

        return {
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "slug": customer.slug,
                "industry": customer.industry,
                "primary_region": customer.primary_region,
            },
            "counts": {
                "watchlists": watchlist_count,
                "watchlist_items": watchlist_item_count,
                "exposure_links": exposure_link_count,
                "suppliers": supplier_count,
                "facilities": facility_count,
                "customer_assets": asset_count,
                "alerts_total": alert_count,
                "alerts_open": open_alert_count,
                "active_events": active_event_count,
                **shared_object_counts,
            },
            "onboarding": onboarding,
        }
