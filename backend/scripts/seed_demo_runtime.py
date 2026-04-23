import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.domain import Document, Entity, EventCluster, MarketPoint, MarketSeries, Source  # noqa: E402
from app.models.strategic_scenario import StrategicScenario  # noqa: E402
from app.models.v2 import (  # noqa: E402
    CommodityV2,
    CustomerAssetV2,
    ExposureLinkV2,
    FacilityV2,
    PortV2,
    RouteV2,
    SupplierV2,
    WatchlistItemV2,
)
from app.services.alert_service_v2 import AlertServiceV2  # noqa: E402
from app.services.backtest_service_v2 import BacktestServiceV2  # noqa: E402
from app.services.customer_service_v2 import CustomerServiceV2  # noqa: E402
from app.services.evaluation_service_v2 import EvaluationServiceV2  # noqa: E402
from app.services.event_service_v2 import EventServiceV2  # noqa: E402
from app.services.market_service import MarketService  # noqa: E402
from app.services.nexus_service import NexusService  # noqa: E402


def ensure_source(db, name: str, source_type: str, url: str, reliability: float) -> Source:
    source = db.query(Source).filter(Source.name == name).first()
    if source:
        return source
    source = Source(
        name=name,
        source_type=source_type,
        url=url,
        reliability_score=reliability,
    )
    db.add(source)
    db.flush()
    return source


def ensure_entity(db, name: str, entity_type: str) -> Entity:
    entity = db.query(Entity).filter(Entity.name == name).first()
    if entity:
        return entity
    entity = Entity(name=name, entity_type=entity_type, metadata_info={})
    db.add(entity)
    db.flush()
    return entity


def ensure_scenario(db, *, topic: str, region: str, sector: str, risk_score: float, status: str, impact: str, count: int) -> None:
    scenario = db.query(StrategicScenario).filter(StrategicScenario.topic == topic).first()
    now = datetime.utcnow()
    if not scenario:
        scenario = StrategicScenario(
            topic=topic,
            region=region,
            sector=sector,
            risk_score=risk_score,
            status=status,
            impact_magnitude=impact,
            last_signal_at=now,
            created_at=now,
            metrics_cache={"signal_count": count, "trend": [max(risk_score - 0.1, 0.1), risk_score]},
        )
        db.add(scenario)
        return
    scenario.region = region
    scenario.sector = sector
    scenario.risk_score = risk_score
    scenario.status = status
    scenario.impact_magnitude = impact
    scenario.last_signal_at = now
    scenario.metrics_cache = {"signal_count": count, "trend": [max(risk_score - 0.1, 0.1), risk_score]}


def ensure_cluster_with_docs(db, *, title: str, description: str, summary: str, documents: list[dict]) -> EventCluster:
    cluster = db.query(EventCluster).filter(EventCluster.title == title).first()
    if not cluster:
        cluster = EventCluster(title=title, description=description, summary=summary, created_at=datetime.utcnow())
        db.add(cluster)
        db.flush()
    else:
        cluster.description = description
        cluster.summary = summary

    for payload in documents:
        doc = db.query(Document).filter(Document.external_id == payload["external_id"]).first()
        if doc:
            continue
        doc = Document(
            source_id=payload["source"].id,
            external_id=payload["external_id"],
            title=payload["title"],
            content=payload["content"],
            url=payload["url"],
            published_at=payload["published_at"],
            normalized_at=datetime.utcnow(),
            raw_data={"seeded": True, "topic": title},
            event_cluster_id=cluster.id,
        )
        db.add(doc)
        db.flush()
        for entity in payload["entities"]:
            doc.entities.append(entity)
    db.flush()
    return cluster


def ensure_watchlist_item(db, watchlist, entity_v2, item_type: str, criticality: float) -> None:
    existing = (
        db.query(WatchlistItemV2)
        .filter(
            WatchlistItemV2.watchlist_id == watchlist.id,
            WatchlistItemV2.entity_id == entity_v2.id,
            WatchlistItemV2.item_type == item_type,
        )
        .first()
    )
    if existing:
        return
    db.add(
        WatchlistItemV2(
            watchlist_id=watchlist.id,
            entity_id=entity_v2.id,
            item_type=item_type,
            criticality_score=criticality,
            created_at=datetime.utcnow(),
        )
    )


def ensure_exposure_link(db, *, customer_id: str, source_object_type: str, source_object_id: str, target_entity_id: str, relationship_type: str, criticality: float, weight: float, confidence: float) -> None:
    existing = (
        db.query(ExposureLinkV2)
        .filter(
            ExposureLinkV2.customer_id == customer_id,
            ExposureLinkV2.source_object_type == source_object_type,
            ExposureLinkV2.source_object_id == source_object_id,
            ExposureLinkV2.target_entity_id == target_entity_id,
        )
        .first()
    )
    if existing:
        return
    db.add(
        ExposureLinkV2(
            customer_id=customer_id,
            source_object_type=source_object_type,
            source_object_id=source_object_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            criticality_score=criticality,
            exposure_weight=weight,
            confidence_score=confidence,
            created_at=datetime.utcnow(),
        )
    )


def ensure_market_series_points(db) -> None:
    seeded = [
        ("CL=F", "Crude Oil", "commodity", 83.0),
        ("GC=F", "Gold Spot", "commodity", 2320.0),
        ("^GSPC", "S&P 500", "index", 5200.0),
        ("^NSEI", "NIFTY 50", "index", 22400.0),
        ("^BSESN", "BSE SENSEX", "index", 73900.0),
    ]
    for ticker, name, asset_class, base in seeded:
        series = db.query(MarketSeries).filter(MarketSeries.ticker == ticker).first()
        if not series:
            series = MarketSeries(ticker=ticker, name=name, asset_class=asset_class)
            db.add(series)
            db.flush()
        point_count = db.query(MarketPoint).filter(MarketPoint.series_id == series.id).count()
        if point_count >= 48:
            continue
        start = datetime.utcnow() - timedelta(hours=48)
        for idx in range(48):
            ts = start + timedelta(hours=idx)
            value = round(base + ((idx % 7) - 3) * 1.15 + idx * 0.08, 2)
            db.add(
                MarketPoint(
                    series_id=series.id,
                    timestamp=ts,
                    value=value,
                    volume=1000 + idx * 25,
                )
            )


def seed() -> None:
    db = SessionLocal()
    try:
        # The demo runtime depends on a blend of v2 and legacy SQLAlchemy models.
        # Alembic creates the v2 schema; create_all fills in any remaining mapped
        # legacy/demo tables so local boot is deterministic from a blank volume.
        Base.metadata.create_all(bind=db.get_bind())

        customer_service = CustomerServiceV2(db)
        event_service = EventServiceV2(db)
        alert_service = AlertServiceV2(db)
        evaluation_service = EvaluationServiceV2(db)
        backtest_service = BacktestServiceV2(db)
        nexus_service = NexusService(db)

        customer = customer_service.get_or_create_demo_customer()
        watchlists = {row.watchlist_type: row for row in customer.watchlists}

        reuters = ensure_source(db, "Reuters World", "news", "https://www.reuters.com/world/", 0.95)
        lloyds = ensure_source(db, "Lloyd's List", "shipping", "https://lloydslist.com/", 0.9)
        ft = ensure_source(db, "Financial Times", "news", "https://www.ft.com/world", 0.92)

        red_sea = ensure_entity(db, "Red Sea", "location")
        suez = ensure_entity(db, "Suez Canal", "location")
        rotterdam = ensure_entity(db, "Port of Rotterdam", "location")
        taiwan = ensure_entity(db, "Taiwan", "location")
        tsmc = ensure_entity(db, "TSMC", "organization")
        rare_earths = ensure_entity(db, "Rare Earth Minerals", "commodity")
        lng = ensure_entity(db, "Liquefied Natural Gas", "commodity")
        brent = ensure_entity(db, "Brent Crude", "commodity")
        china = ensure_entity(db, "China", "location")

        now = datetime.utcnow()
        red_sea_cluster = ensure_cluster_with_docs(
            db,
            title="Red Sea transit disruption pressures shipping and energy flows",
            description="Commercial shipping through the Red Sea faces renewed disruption, affecting Europe-bound routes and energy costs.",
            summary="Transit risk in the Red Sea is increasing insurance costs, delaying cargo flows, and lifting crude and LNG sensitivity.",
            documents=[
                {
                    "source": reuters,
                    "external_id": "seed-redsea-1",
                    "title": "Insurers raise premiums as Red Sea attacks disrupt vessel schedules",
                    "content": "Insurers and shippers report renewed disruption in the Red Sea and Suez Canal corridor. Port of Rotterdam logistics planners are monitoring delays while Brent Crude and LNG freight premiums move higher.",
                    "url": "https://example.com/red-sea-1",
                    "published_at": now - timedelta(hours=14),
                    "entities": [red_sea, suez, rotterdam, brent, lng],
                },
                {
                    "source": lloyds,
                    "external_id": "seed-redsea-2",
                    "title": "Europe-bound container route sees cascading delay risk",
                    "content": "The Asia-Europe Suez route is seeing detours and longer cycle times. Operators say the Red Sea chokepoint remains unstable and could affect downstream facilities tied to Rotterdam inbound cargo.",
                    "url": "https://example.com/red-sea-2",
                    "published_at": now - timedelta(hours=9),
                    "entities": [red_sea, suez, rotterdam],
                },
            ],
        )

        taiwan_cluster = ensure_cluster_with_docs(
            db,
            title="Taiwan export-control review heightens semiconductor supply risk",
            description="A new policy review around advanced chip exports is increasing supply-chain uncertainty for semiconductor customers.",
            summary="Export-control scrutiny around Taiwan and China is elevating operational risk for firms dependent on TSMC and advanced manufacturing flows.",
            documents=[
                {
                    "source": ft,
                    "external_id": "seed-taiwan-1",
                    "title": "Policy review puts TSMC-linked supply chains on alert",
                    "content": "A Taiwan export-control review and new China policy scrutiny are pushing manufacturers to re-evaluate dependence on TSMC. Analysts warn of renewed semiconductor supply concentration risk.",
                    "url": "https://example.com/taiwan-1",
                    "published_at": now - timedelta(hours=11),
                    "entities": [taiwan, china, tsmc],
                },
                {
                    "source": reuters,
                    "external_id": "seed-taiwan-2",
                    "title": "Chip buyers assess buffer inventory after Taiwan policy signal",
                    "content": "Industrial buyers are assessing buffer inventory after a Taiwan policy signal raised questions for TSMC lead times and downstream manufacturing continuity.",
                    "url": "https://example.com/taiwan-2",
                    "published_at": now - timedelta(hours=7),
                    "entities": [taiwan, tsmc],
                },
            ],
        )

        rare_earth_cluster = ensure_cluster_with_docs(
            db,
            title="Rare earth export review unsettles advanced manufacturing inputs",
            description="Rare earth export reviews are emerging as a new pressure point for electronics and industrial inputs.",
            summary="Rare earth restrictions could tighten advanced manufacturing inputs and push procurement teams toward contingency sourcing.",
            documents=[
                {
                    "source": ft,
                    "external_id": "seed-rareearth-1",
                    "title": "Rare earth review triggers sourcing contingency plans",
                    "content": "Procurement teams are revisiting contingency plans as China signals tighter review of Rare Earth Minerals exports used in electronics, batteries and industrial systems.",
                    "url": "https://example.com/rare-earth-1",
                    "published_at": now - timedelta(hours=5),
                    "entities": [china, rare_earths],
                }
            ],
        )

        ensure_scenario(
            db,
            topic="Red Sea conflict escalation",
            region="MENA",
            sector="LOGISTICS",
            risk_score=0.84,
            status="CRITICAL",
            impact="HIGH",
            count=18,
        )
        ensure_scenario(
            db,
            topic="Taiwan export control review",
            region="APAC",
            sector="TECH",
            risk_score=0.77,
            status="ACTIVE",
            impact="HIGH",
            count=12,
        )
        ensure_scenario(
            db,
            topic="Rare earth mineral export pressure",
            region="APAC",
            sector="INDUSTRIALS",
            risk_score=0.66,
            status="ACTIVE",
            impact="MODERATE",
            count=9,
        )
        ensure_scenario(
            db,
            topic="LNG insurance premium shock",
            region="EMEA",
            sector="ENERGY",
            risk_score=0.58,
            status="EMERGING",
            impact="MODERATE",
            count=7,
        )

        ensure_market_series_points(db)
        db.commit()

        # Sync clusters into canonical events and entities.
        for cluster in [red_sea_cluster, taiwan_cluster, rare_earth_cluster]:
            event_service.sync_cluster(cluster)
        db.commit()

        red_sea_v2 = event_service.ensure_entity_v2(red_sea)
        rotterdam_v2 = event_service.ensure_entity_v2(rotterdam)
        taiwan_v2 = event_service.ensure_entity_v2(taiwan)
        tsmc_v2 = event_service.ensure_entity_v2(tsmc)
        rare_earths_v2 = event_service.ensure_entity_v2(rare_earths)
        brent_v2 = event_service.ensure_entity_v2(brent)

        if "events" in watchlists:
            ensure_watchlist_item(db, watchlists["events"], red_sea_v2, "event_region", 0.95)
            ensure_watchlist_item(db, watchlists["events"], taiwan_v2, "event_region", 0.9)
        if "suppliers" in watchlists:
            ensure_watchlist_item(db, watchlists["suppliers"], tsmc_v2, "supplier", 0.98)
        if "commodities" in watchlists:
            ensure_watchlist_item(db, watchlists["commodities"], brent_v2, "commodity", 0.8)
            ensure_watchlist_item(db, watchlists["commodities"], rare_earths_v2, "commodity", 0.82)
        if "geographies" in watchlists:
            ensure_watchlist_item(db, watchlists["geographies"], rotterdam_v2, "port", 0.75)

        supplier = db.query(SupplierV2).filter(SupplierV2.customer_id == customer.id, SupplierV2.supplier_name == "TSMC").first()
        if not supplier:
            supplier = SupplierV2(
                customer_id=customer.id,
                entity_id=tsmc_v2.id,
                supplier_name="TSMC",
                tier_level=1,
                country_code="TW",
                criticality_score=0.98,
                created_at=now,
                updated_at=now,
            )
            db.add(supplier)
            db.flush()

        facility = db.query(FacilityV2).filter(FacilityV2.customer_id == customer.id, FacilityV2.facility_name == "Rotterdam Distribution Hub").first()
        if not facility:
            facility = FacilityV2(
                customer_id=customer.id,
                entity_id=rotterdam_v2.id,
                facility_name="Rotterdam Distribution Hub",
                facility_type="distribution_center",
                country_code="NL",
                lat=51.95,
                lng=4.14,
                criticality_score=0.86,
                created_at=now,
                updated_at=now,
            )
            db.add(facility)
            db.flush()

        red_sea_port = db.query(PortV2).filter(PortV2.port_name == "Port of Rotterdam").first()
        if not red_sea_port:
            red_sea_port = PortV2(
                entity_id=rotterdam_v2.id,
                port_code="NLRTM",
                port_name="Port of Rotterdam",
                country_code="NL",
                lat=51.95,
                lng=4.14,
                created_at=now,
                updated_at=now,
            )
            db.add(red_sea_port)
            db.flush()

        route = db.query(RouteV2).filter(RouteV2.route_name == "Asia-Europe Suez Route").first()
        if not route:
            route = RouteV2(
                route_name="Asia-Europe Suez Route",
                route_type="shipping_lane",
                destination_port_id=red_sea_port.id,
                created_at=now,
                updated_at=now,
            )
            db.add(route)
            db.flush()

        commodity = db.query(CommodityV2).filter(CommodityV2.commodity_name == "Brent Crude").first()
        if not commodity:
            commodity = CommodityV2(
                entity_id=brent_v2.id,
                commodity_code="BRENT",
                commodity_name="Brent Crude",
                sector="energy",
                created_at=now,
                updated_at=now,
            )
            db.add(commodity)
            db.flush()

        customer_asset = db.query(CustomerAssetV2).filter(CustomerAssetV2.customer_id == customer.id, CustomerAssetV2.asset_label == "Semiconductor Assembly Line A").first()
        if not customer_asset:
            customer_asset = CustomerAssetV2(
                customer_id=customer.id,
                entity_id=tsmc_v2.id,
                asset_label="Semiconductor Assembly Line A",
                asset_type="manufacturing_line",
                criticality_score=0.94,
                created_at=now,
                updated_at=now,
            )
            db.add(customer_asset)
            db.flush()

        ensure_exposure_link(
            db,
            customer_id=customer.id,
            source_object_type="route",
            source_object_id=route.id,
            target_entity_id=red_sea_v2.id,
            relationship_type="depends_on",
            criticality=0.92,
            weight=0.9,
            confidence=0.88,
        )
        ensure_exposure_link(
            db,
            customer_id=customer.id,
            source_object_type="facility",
            source_object_id=facility.id,
            target_entity_id=rotterdam_v2.id,
            relationship_type="receives_through",
            criticality=0.82,
            weight=0.75,
            confidence=0.84,
        )
        ensure_exposure_link(
            db,
            customer_id=customer.id,
            source_object_type="supplier",
            source_object_id=supplier.id,
            target_entity_id=taiwan_v2.id,
            relationship_type="operates_in",
            criticality=0.97,
            weight=0.95,
            confidence=0.9,
        )
        ensure_exposure_link(
            db,
            customer_id=customer.id,
            source_object_type="customer_asset",
            source_object_id=customer_asset.id,
            target_entity_id=tsmc_v2.id,
            relationship_type="depends_on",
            criticality=0.98,
            weight=0.97,
            confidence=0.93,
        )
        ensure_exposure_link(
            db,
            customer_id=customer.id,
            source_object_type="commodity",
            source_object_id=commodity.id,
            target_entity_id=brent_v2.id,
            relationship_type="requires",
            criticality=0.76,
            weight=0.7,
            confidence=0.8,
        )
        ensure_exposure_link(
            db,
            customer_id=customer.id,
            source_object_type="commodity",
            source_object_id=commodity.id,
            target_entity_id=rare_earths_v2.id,
            relationship_type="correlates_with",
            criticality=0.62,
            weight=0.58,
            confidence=0.7,
        )
        db.commit()

        # Create alerts and evaluation artifacts.
        alert_service.generate_for_customer(customer)
        events = event_service.list_events(limit=20, skip=0)
        for event in events[:2]:
            existing_labels = evaluation_service.list_labels(event.id, customer.id)
            if existing_labels:
                continue
            evaluation_service.add_label(
                event_id=event.id,
                customer_id=customer.id,
                alert_id=None,
                label_type="event_was_material",
                label_value="true",
                notes="Seeded demo label for dashboard validation.",
                labeled_by="system-seed",
            )
            evaluation_service.add_label(
                event_id=event.id,
                customer_id=customer.id,
                alert_id=None,
                label_type="alert_was_useful",
                label_value="true",
                notes="Seeded useful alert outcome.",
                labeled_by="system-seed",
            )
            evaluation_service.add_label(
                event_id=event.id,
                customer_id=customer.id,
                alert_id=None,
                label_type="lead_time_hours",
                label_value="36",
                notes="Seeded lead time estimate.",
                labeled_by="system-seed",
            )

        runs = backtest_service.list_runs(customer.id, limit=1)
        if not runs:
            backtest_service.create_run(
                run_name="Demo baseline validation",
                customer=customer,
                config={"source": "seed_demo_runtime", "include_customer_scope": True},
            )

        nexus_service.sync_knowledge_graph()
        db.commit()
        print("GeoSyn demo runtime seed complete.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
