from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.services.customer_service_v2 import CustomerServiceV2


def get_current_customer(
    db: Session = Depends(get_db),
    x_customer_slug: str | None = Header(default=None),
) -> CustomerV2:
    service = CustomerServiceV2(db)
    if x_customer_slug:
        customer = service.get_by_slug(x_customer_slug)
        if customer:
            return customer
    return service.get_or_create_demo_customer()
