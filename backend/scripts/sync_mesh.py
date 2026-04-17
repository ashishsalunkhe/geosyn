import asyncio
import sys
import os
from datetime import datetime

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base # Import Base with all models registered
from app.db.session import SessionLocal, engine
from app.services.ingestion_service import IngestionService
from app.services.market_service import MarketService
from app.services.clustering_service import ClusteringService
from app.services.nexus_service import NexusService

async def main():
    print(f"--- GeoSyn Mesh Sync Started [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---")
    
    # Ensure local schema is initialized (Phase 2 Hardening)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Institutional Macro & Markets
        print("[1/5] Syncing Markets...")
        market_service = MarketService(db)
        await market_service.sync_all_markets()

        # 2. Institutional Macro (IMF, WB, FRED Labor/GDP)
        print("[2/5] Syncing Institutional Macro Anchors (IMF, WB, Labor)...")
        ingestion_service = IngestionService(db)
        await ingestion_service.ingest_institutional_macro()
        
        # 3. Intelligence Ingestion (GDELT / News)
        print("[3/5] Ingesting Intelligence Signals (GDELT / News)...")
        await ingestion_service.ingest_latest_news(sync_gdelt=True)
        
        # 4. Local AI Clustering (Semantic Mesh)
        print("[4/5] Running Local AI Semantic Clustering...")
        cluster_service = ClusteringService(db)
        cluster_service.run_clustering()
        
        # 5. Knowledge Graph Synthesis (Causal Nexus)
        print("[5/5] Rebuilding Causal Nexus Graph...")
        nexus_service = NexusService(db)
        nexus_service.sync_knowledge_graph()
        
        print(f"--- GeoSyn Mesh Sync Complete! [{datetime.now().strftime('%H:%M:%S')}] ---")
    except Exception as e:
        print(f"FAILED: Mesh Sync error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
