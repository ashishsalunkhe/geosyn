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

async def proactive_polling_loop():
    """Background loop that triggers ingestion and generating alerts every 5 mins."""
    loop_counter = 0
    while True:
        try:
            # Sync GDELT only once per hour (skip the immediate boot sequence to prevent deadlock)
            do_gdelt_sync = (loop_counter > 0 and loop_counter % 12 == 0)
            print(f"GeoSyn: Initiating 5-Minute Proactive Sync... (Hourly GDELT: {do_gdelt_sync})")
            
            db = SessionLocal()
            try:
                # 1. Sync Markets
                market_service = MarketService(db)
                await market_service.sync_all_markets()
                
                # 2. Ingest OSINT/GDELT/RSS
                ingestion_service = IngestionService(db)
                await ingestion_service.ingest_latest_news(sync_gdelt=do_gdelt_sync)
                
                # 3. Cluster & Detect Shocks
                cluster_service = ClusteringService(db)
                cluster_service.run_clustering()
                
                # 4. Sync Knowledge Graph (Causal Nexus)
                nexus_service = NexusService(db)
                nexus_service.sync_knowledge_graph()
                
                print("GeoSyn: 5-Minute Sync Complete. Alerts Updated.")
            finally:
                db.close()
                
            loop_counter += 1
        except Exception as e:
            print(f"GeoSyn Polling Error: {e}")
        
        await asyncio.sleep(300)

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
