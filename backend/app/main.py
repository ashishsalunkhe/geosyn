import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.services.ingestion_service import IngestionService
from app.services.market_service import MarketService
from app.services.clustering_service import ClusteringService
from app.services.nexus_service import NexusService
from app.services.divergence_service import DivergenceService

async def proactive_polling_loop():
    """Industrial background loop that triggers multi-tiered ingestion every 15 mins."""
    loop_counter = 0
    while True:
        try:
            db = SessionLocal()
            try:
                # CYCLE 1: High-Frequency (Every 15 mins)
                print(f"GeoSyn: [H-Freq] Initiating Signal Sync... (Batch #{loop_counter})")
                
                # 1. Sync Markets
                market_service = MarketService(db)
                await market_service.sync_all_markets()
                
                # 2. Ingest OSINT/GDELT
                ingestion_service = IngestionService(db)
                await ingestion_service.ingest_latest_news(sync_gdelt=True)
                
                # CYCLE 2: Institutional Macro (Every 30 mins, i.e., every 2nd batch)
                if loop_counter % 2 == 0:
                    print(f"GeoSyn: [Anchor] Initiating Institutional Macro Sync... (IMF, WB, Labor, GDP)")
                    await ingestion_service.ingest_institutional_macro()
                    await ingestion_service.ingest_compliance_signals()
                    
                    # 3. Tactical Divergence Analysis (Surprise Detection)
                    divergence_service = DivergenceService(db)
                    divergence_service.analyze_causal_shocks()

                # 3. Local AI Clustering & Analysis
                cluster_service = ClusteringService(db)
                cluster_service.run_clustering()
                
                # 4. Sync Knowledge Graph (Causal Nexus)
                nexus_service = NexusService(db)
                nexus_service.sync_knowledge_graph()
                
                print(f"GeoSyn: Batch #{loop_counter} Complete. Mesh Synchronized.")
            finally:
                db.close()
                
            loop_counter += 1
        except Exception as e:
            print(f"GeoSyn Background Sync Error: {e}")
        
        # 15 minute interval = 900 seconds
        await asyncio.sleep(900)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    # Background worker reinstated
    polling_task = asyncio.create_task(proactive_polling_loop())
    yield
    # Shutdown: Clean up task
    polling_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to GeoSyn API"}

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
