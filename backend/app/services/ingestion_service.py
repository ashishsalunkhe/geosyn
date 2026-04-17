from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Type
from app.ingestion.base import BaseProvider
from app.ingestion.gdelt_provider import GDELTProvider
from app.ingestion.event_registry_provider import EventRegistryProvider
from app.ingestion.rss_provider import RSSProvider
from app.pipelines.normalization import NormalizationPipeline
from app.models.domain import Document, Source
from app.db.session import SessionLocal

from app.ingestion.osint_provider import OSINTProvider
from app.ingestion.imf_provider import IMFProvider
from app.ingestion.world_bank_provider import WorldBankProvider
from app.ingestion.fred_provider import FREDProvider

class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = NormalizationPipeline()
        self.osint_provider = OSINTProvider()

    def run_osint_sync(self, query: str = "") -> List[Document]:
        """
        Specialized ingestion for OSINT chatter.
        """
        source = self.db.query(Source).filter(Source.name == "OSINT-SEC MONITOR").first()
        if not source:
            source = Source(name="OSINT-SEC MONITOR", source_type="osint", reliability_score=0.8)
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
            
        raw_osint = self.osint_provider.fetch_social_chatter(query=query)
        ingested = []
        for raw in raw_osint:
            existing = self.db.query(Document).filter(Document.external_id == raw["external_id"]).first()
            if existing: continue
            
            # Use raw data directly since it's already structured by provider
            new_doc = Document(
                title=raw["title"],
                content=raw["content"],
                url=raw["url"],
                published_at=datetime.fromisoformat(raw["published_at"].replace("Z", "+00:00")),
                external_id=raw["external_id"],
                source_id=source.id,
                raw_data=raw
            )
            self.db.add(new_doc)
            ingested.append(new_doc)
            
        self.db.commit()
        return ingested

    async def ingest_institutional_macro(self):
        """
        Syncs high-fidelity institutional data (IMF, World Bank, BLS/BEA via FRED).
        Executed in 30-minute batches (as approved).
        """
        print(f"GeoSyn: Running Institutional Macro Sync... (IMF, WB, Labor, GDP)")
        
        imf = IMFProvider()
        wb = WorldBankProvider()
        fred = FREDProvider()
        
        # 1. Sync IMF (Growth, Debt, Inflation)
        try:
            self.run_ingestion(imf)
        except Exception as e:
            print(f"IMF Macro Sync Error: {e}")
            
        # 2. Sync World Bank (Trade, Energy)
        try:
            self.run_ingestion(wb)
        except Exception as e:
            print(f"World Bank Macro Sync Error: {e}")
            
        # 3. Sync FRED (Labor, GDP, Rates)
        try:
            self.run_ingestion(fred)
        except Exception as e:
            print(f"FRED Macro Sync Error: {e}")
            
        self.db.commit()

    async def ingest_latest_news(self, sync_gdelt: bool = False):
        """
        Automated sync for RSS, OSINT sources, and heavily throttled GDELT sources.
        """
        print(f"GeoSyn: Running News Ingestion Sync... (GDELT: {sync_gdelt})")
        rss = RSSProvider()
        osint = OSINTProvider()
        
        # 1. Sync High-Frequency RSS
        try:
            docs = self.run_ingestion(rss)
        except Exception as e:
            print(f"RSS Sync Error: {e}")
            docs = []
            
        # 2. Sync News Signals (GDELT with Event Registry Fallback)
        if sync_gdelt:
            try:
                print("GeoSyn: Attempting GDELT Sync...")
                gdelt = GDELTProvider()
                docs += self.run_ingestion(gdelt)
            except Exception as e:
                print(f"GeoSyn: GDELT Sync Failed ({e}). Initiating Fallback to Event Registry...")
                try:
                    er = EventRegistryProvider()
                    docs += self.run_ingestion(er)
                except Exception as er_e:
                    print(f"GeoSyn: Event Registry Fallback also failed: {er_e}")
            
        # 3. Sync OSINT
        try:
            docs += self.run_osint_sync()
        except Exception as e:
            print(f"OSINT Sync Error: {e}")
        
        # Detect Alerts from News Shocks
        from app.models.domain import Alert, Entity
        from app.core.tickers import ALL_TRACKED_TICKERS
        
        # Look for documents mentioning our tracked tickers in the last 15 mins
        for ticker in ALL_TRACKED_TICKERS:
            # Check for high-volume mentions of the ticker name
            ticker_name = ticker # Simplification
            new_mentions = self.db.query(Document).join(Document.entities).filter(
                Entity.name.ilike(f"%{ticker_name}%"),
                Document.normalized_at > datetime.utcnow() - timedelta(minutes=15)
            ).all()

            if len(new_mentions) >= 3: # Contextual threshold: 3 news items in 15 mins
                # Create Narrative Alert
                recent_alert = self.db.query(Alert).filter(
                    Alert.ticker == ticker,
                    Alert.type == "narrative_shift",
                    Alert.created_at > datetime.utcnow() - timedelta(minutes=30)
                ).first()

                if not recent_alert:
                    self.db.add(Alert(
                        type="narrative_shift",
                        severity="medium",
                        ticker=ticker,
                        title=f"Narrative Surge: ${ticker}",
                        content=f"Substantial news volume detected regarding ${ticker}. Total items in 15m window: {len(new_mentions)}",
                        context_snippet=new_mentions[0].title,
                        alert_payload={"docs_count": len(new_mentions)}
                    ))
        
        self.db.commit()

    def run_ingestion(self, provider: BaseProvider, query: str = None) -> List[Document]:
        """
        Coordinates the ingestion process for a specific provider.
        """
        # 1. Ensure Source exists in DB
        source = self.db.query(Source).filter(Source.name == provider.provider_name).first()
        if not source:
            source = Source(
                name=provider.provider_name,
                source_type=provider.source_type,
                reliability_score=1.0
            )
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)

        # 2. Fetch raw docs
        raw_docs = provider.fetch_raw_docs(query=query) if query else provider.fetch_raw_docs()
        
        ingested_docs = []
        for raw in raw_docs:
            # Check if already exists by external_id
            existing = self.db.query(Document).filter(
                Document.external_id == raw.get("id"),
                Document.source_id == source.id
            ).first()
            
            if existing:
                continue

            # 3. Normalize
            doc_data = self.pipeline.normalize(raw, source.id)
            
            # 4. Save Document
            new_doc = Document(**doc_data.dict())
            self.db.add(new_doc)
            self.db.flush() # Get ID

            # 5. Extract and Link Entities
            raw_content = doc_data.content or ""
            entities_metadata = self.pipeline.extract_entities(raw_content)
            
            from app.models.domain import Entity
            for ent_meta in entities_metadata:
                # Find or create entity
                entity = self.db.query(Entity).filter(Entity.name == ent_meta["name"]).first()
                if not entity:
                    entity = Entity(
                        name=ent_meta["name"],
                        entity_type=ent_meta["type"]
                    )
                    self.db.add(entity)
                    self.db.flush()
                
                # Link to document
                if entity not in new_doc.entities:
                    new_doc.entities.append(entity)
            
            ingested_docs.append(new_doc)
        
        self.db.commit()
        return ingested_docs
