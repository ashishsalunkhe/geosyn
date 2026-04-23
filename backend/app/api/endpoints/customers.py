from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.services.customer_service_v2 import CustomerServiceV2

router = APIRouter()


@router.get("/me", response_model=dict)
def read_current_customer(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
):
    service = CustomerServiceV2(db)
    return service.get_overview(current_customer)
