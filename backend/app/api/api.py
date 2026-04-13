from fastapi import APIRouter
from app.api.endpoints import documents, events, markets, claims, ingestion, clustering, scenarios, alerts, nexus, intelligence, analytics

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(markets.router, prefix="/markets", tags=["markets"])
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(clustering.router, prefix="/clustering", tags=["clustering"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(nexus.router, prefix="/nexus", tags=["nexus"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
