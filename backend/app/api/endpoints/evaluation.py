from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_customer
from app.db.session import get_db
from app.models.v2 import CustomerV2
from app.services.backtest_service_v2 import BacktestServiceV2

router = APIRouter()


class BacktestRunRequest(BaseModel):
    run_name: str
    include_customer_scope: bool = True


@router.get("/metrics", response_model=dict)
def read_evaluation_metrics(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
    include_customer_scope: bool = True,
) -> Any:
    service = BacktestServiceV2(db)
    customer_id: Optional[str] = current_customer.id if include_customer_scope else None
    return service.compute_metrics(customer_id)


@router.get("/runs", response_model=list[dict])
def list_backtest_runs(
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
    include_customer_scope: bool = True,
) -> Any:
    service = BacktestServiceV2(db)
    customer_id: Optional[str] = current_customer.id if include_customer_scope else None
    runs = service.list_runs(customer_id=customer_id)
    return [service.serialize_run(run) for run in runs]


@router.post("/runs", response_model=dict)
def create_backtest_run(
    payload: BacktestRunRequest,
    db: Session = Depends(get_db),
    current_customer: CustomerV2 = Depends(get_current_customer),
) -> Any:
    service = BacktestServiceV2(db)
    run = service.create_run(
        run_name=payload.run_name,
        customer=current_customer if payload.include_customer_scope else None,
        config={"include_customer_scope": payload.include_customer_scope},
    )
    return service.serialize_run(run)
