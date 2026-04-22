"""
Backfill provenance documents and customer risk scores for the v2 graph/risk layer.

Run from backend/:
    python scripts/backfill_graph_risk_v2.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.domain import Document
from app.models.v2 import CustomerV2, EventV2
from app.services.event_service_v2 import EventServiceV2
from app.services.provenance_service_v2 import ProvenanceServiceV2


def main() -> None:
    db = SessionLocal()
    try:
        provenance = ProvenanceServiceV2(db)
        event_service = EventServiceV2(db)

        documents = db.query(Document).all()
        provenance.backfill_documents(documents)

        customers = db.query(CustomerV2).all()
        events = db.query(EventV2).all()
        risk_count = 0
        for customer in customers:
            for event in events:
                explanation = event_service.explain_event_for_customer(event.id, customer.id)
                if explanation.get("risk_score"):
                    risk_count += 1

        db.commit()
        print(
            f"Backfill complete. Synced {len(documents)} evidence documents and refreshed {risk_count} customer risk scores."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
