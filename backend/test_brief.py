import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.services.timeline_service import TimelineService

db = SessionLocal()
try:
    svc = TimelineService()
    res = svc.generate_intelligence_brief("Red Sea Conflict Escalation", "CL=F", db)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
