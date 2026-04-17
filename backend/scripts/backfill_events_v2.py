import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal  # noqa: E402
from app.models.domain import EventCluster  # noqa: E402
from app.models.v2 import (  # noqa: E402
    EntityV2,
    EventEntityV2,
    EventEvidenceV2,
    EventV2,
    LegacyClusterEventMapV2,
)


def ensure_entity_v2(db, legacy_entity):
    existing = (
        db.query(EntityV2)
        .filter(EntityV2.legacy_entity_id == legacy_entity.id)
        .first()
    )
    if existing:
        return existing

    entity = EntityV2(
        legacy_entity_id=legacy_entity.id,
        entity_type=(legacy_entity.entity_type or "unknown").lower(),
        canonical_name=legacy_entity.name,
        display_name=legacy_entity.name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(entity)
    db.flush()
    return entity


def backfill() -> None:
    db = SessionLocal()
    try:
        clusters = db.query(EventCluster).all()
        migrated = 0

        for cluster in clusters:
            mapping = (
                db.query(LegacyClusterEventMapV2)
                .filter(LegacyClusterEventMapV2.legacy_cluster_id == cluster.id)
                .first()
            )
            if mapping:
                continue

            docs = sorted(
                cluster.documents,
                key=lambda d: d.published_at or cluster.created_at or datetime.utcnow(),
            )
            first_seen = docs[0].published_at if docs and docs[0].published_at else cluster.created_at or datetime.utcnow()
            last_seen = docs[-1].published_at if docs and docs[-1].published_at else first_seen

            event = EventV2(
                canonical_title=cluster.title or f"Cluster {cluster.id}",
                event_type="legacy_cluster",
                event_subtype=None,
                status="active",
                first_seen_at=first_seen,
                last_seen_at=last_seen,
                severity_score=None,
                confidence_score=None,
                summary_text=cluster.summary or cluster.description,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(event)
            db.flush()

            primary_doc_id = docs[0].id if docs else None
            attached_entity_ids = set()
            for doc in docs:
                evidence = EventEvidenceV2(
                    event_id=event.id,
                    legacy_document_id=doc.id,
                    contribution_type="legacy_cluster_backfill",
                    relevance_score=1.0,
                    is_primary=(doc.id == primary_doc_id),
                    created_at=datetime.utcnow(),
                )
                db.add(evidence)

                for legacy_entity in doc.entities:
                    entity_v2 = ensure_entity_v2(db, legacy_entity)
                    dedupe_key = (event.id, entity_v2.id, "mentioned")
                    if dedupe_key in attached_entity_ids:
                        continue
                    exists = (
                        db.query(EventEntityV2)
                        .filter(
                            EventEntityV2.event_id == event.id,
                            EventEntityV2.entity_id == entity_v2.id,
                            EventEntityV2.event_role == "mentioned",
                        )
                        .first()
                    )
                    if not exists:
                        attached_entity_ids.add(dedupe_key)
                        db.add(
                            EventEntityV2(
                                event_id=event.id,
                                entity_id=entity_v2.id,
                                event_role="mentioned",
                                confidence_score=1.0,
                                is_primary=False,
                                created_at=datetime.utcnow(),
                            )
                        )

            db.add(
                LegacyClusterEventMapV2(
                    legacy_cluster_id=cluster.id,
                    event_id=event.id,
                    migrated_at=datetime.utcnow(),
                )
            )
            migrated += 1

        db.commit()
        print(f"Backfill complete. Migrated {migrated} legacy clusters into canonical events.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
