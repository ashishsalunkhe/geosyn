"""
Create an initial evaluation backtest run for the current local dataset.

Run from backend/:
    python scripts/backfill_backtest_runs_v2.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.v2 import CustomerV2
from app.services.backtest_service_v2 import BacktestServiceV2


def main() -> None:
    db = SessionLocal()
    try:
        service = BacktestServiceV2(db)
        customer = db.query(CustomerV2).first()
        run = service.create_run(
            run_name="initial-local-backtest",
            customer=customer,
            config={"source": "backfill_script", "scope": "customer"},
        )
        print(f"Backtest run created: {run.id} ({run.run_name})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
