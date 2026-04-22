"""
Backfill timeline rows for canonical v2 events from their evidence documents.

Run from backend/:
    python scripts/backfill_event_timelines_v2.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.v2 import EventV2
from app.services.event_timeline_service_v2 import EventTimelineServiceV2


def main() -> None:
    db = SessionLocal()
    try:
        service = EventTimelineServiceV2(db)
        total = 0
        for event in db.query(EventV2).all():
            rows = service.ensure_timelines_for_event(event)
            total += len(rows)
        db.commit()
        print(f"Timeline backfill complete. Processed {total} timeline rows across canonical events.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
