import asyncio
import logging

from app.core.celery_app import celery_app
from app.core.metrics import task_runtime_seconds
from app.db.session import SessionLocal
from app.models.v2 import CustomerV2
from app.services.clustering_service import ClusteringService
from app.services.divergence_service import DivergenceService
from app.services.ingestion_service import IngestionService
from app.services.market_service import MarketService
from app.services.nexus_service import NexusService
from app.services.alert_service_v2 import AlertServiceV2


logger = logging.getLogger(__name__)


def _run_async(coro):
    return asyncio.run(coro)


@celery_app.task(name="app.workers.tasks.run_high_frequency_sync")
def run_high_frequency_sync():
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_high_frequency_sync").time():
            logger.info("GeoSyn worker: starting high-frequency sync batch")
            market_service = MarketService(db)
            ingestion_service = IngestionService(db)
            cluster_service = ClusteringService(db)
            nexus_service = NexusService(db)

            _run_async(market_service.sync_all_markets())
            _run_async(ingestion_service.ingest_latest_news(sync_gdelt=True))
            cluster_service.run_clustering()
            nexus_service.sync_knowledge_graph()
            logger.info("GeoSyn worker: completed high-frequency sync batch")
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_anchor_sync")
def run_anchor_sync():
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_anchor_sync").time():
            logger.info("GeoSyn worker: starting anchor sync batch")
            ingestion_service = IngestionService(db)
            divergence_service = DivergenceService(db)
            cluster_service = ClusteringService(db)
            nexus_service = NexusService(db)

            _run_async(ingestion_service.ingest_institutional_macro())
            _run_async(ingestion_service.ingest_compliance_signals())
            divergence_service.analyze_causal_shocks()
            cluster_service.run_clustering()
            nexus_service.sync_knowledge_graph()
            logger.info("GeoSyn worker: completed anchor sync batch")
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_market_sync")
def run_market_sync():
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_market_sync").time():
            logger.info("GeoSyn worker: starting market sync")
            market_service = MarketService(db)
            _run_async(market_service.sync_all_markets())
            logger.info("GeoSyn worker: completed market sync")
            return {"status": "success"}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_news_ingestion")
def run_news_ingestion(sync_gdelt: bool = True):
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_news_ingestion").time():
            logger.info("GeoSyn worker: starting news ingestion")
            ingestion_service = IngestionService(db)
            _run_async(ingestion_service.ingest_latest_news(sync_gdelt=sync_gdelt))
            logger.info("GeoSyn worker: completed news ingestion")
            return {"status": "success", "sync_gdelt": sync_gdelt}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_compliance_ingestion")
def run_compliance_ingestion(query: str = ""):
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_compliance_ingestion").time():
            logger.info("GeoSyn worker: starting compliance ingestion")
            ingestion_service = IngestionService(db)
            _run_async(ingestion_service.ingest_compliance_signals(query=query))
            logger.info("GeoSyn worker: completed compliance ingestion")
            return {"status": "success", "query": query}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_clustering")
def run_clustering():
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_clustering").time():
            logger.info("GeoSyn worker: starting clustering")
            cluster_service = ClusteringService(db)
            event_clusters = cluster_service.run_clustering()
            logger.info("GeoSyn worker: completed clustering")
            return {"status": "success", "cluster_count": len(event_clusters)}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_nexus_sync")
def run_nexus_sync():
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_nexus_sync").time():
            logger.info("GeoSyn worker: starting nexus sync")
            nexus_service = NexusService(db)
            nexus_service.sync_knowledge_graph()
            logger.info("GeoSyn worker: completed nexus sync")
            return {"status": "success"}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_alert_generation")
def run_alert_generation(customer_id: str):
    db = SessionLocal()
    try:
        with task_runtime_seconds.labels("run_alert_generation").time():
            logger.info("GeoSyn worker: starting alert generation for customer %s", customer_id)
            customer = db.query(CustomerV2).filter(CustomerV2.id == customer_id).first()
            if not customer:
                raise ValueError(f"Customer not found: {customer_id}")
            alert_service = AlertServiceV2(db)
            result = alert_service.generate_for_customer(customer)
            logger.info("GeoSyn worker: completed alert generation for customer %s", customer_id)
            return result
    finally:
        db.close()
