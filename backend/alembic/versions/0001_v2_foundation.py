"""v2 foundation

Revision ID: 0001_v2_foundation
Revises:
Create Date: 2026-04-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "1_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entities_v2",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("legacy_entity_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("canonical_name", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("region_code", sa.String(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("legacy_entity_id"))
    op.create_index("ix_entities_v2_legacy_entity_id", "entities_v2", ["legacy_entity_id"])
    op.create_index("ix_entities_v2_entity_type", "entities_v2", ["entity_type"])
    op.create_index("ix_entities_v2_canonical_name", "entities_v2", ["canonical_name"])

    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("canonical_title", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=True),
        sa.Column("event_subtype", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("primary_geo_entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("severity_score", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_events_canonical_title", "events", ["canonical_title"])
    op.create_index("ix_events_status", "events", ["status"])
    op.create_index("ix_events_first_seen_at", "events", ["first_seen_at"])
    op.create_index("ix_events_last_seen_at", "events", ["last_seen_at"])

    op.create_table(
        "event_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("legacy_document_id", sa.Integer(), nullable=False),
        sa.Column("contribution_type", sa.String(), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("event_id", "legacy_document_id", name="uq_event_evidence_event_legacy_document"))
    op.create_index("ix_event_evidence_event_id", "event_evidence", ["event_id"])
    op.create_index("ix_event_evidence_legacy_document_id", "event_evidence", ["legacy_document_id"])

    op.create_table(
        "event_entities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=False),
        sa.Column("event_role", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("event_id", "entity_id", "event_role", name="uq_event_entities_event_entity_role"))
    op.create_index("ix_event_entities_event_id", "event_entities", ["event_id"])
    op.create_index("ix_event_entities_entity_id", "event_entities", ["entity_id"])
    op.create_index("ix_event_entities_event_role", "event_entities", ["event_role"])

    op.create_table(
        "legacy_cluster_event_map",
        sa.Column("legacy_cluster_id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("migrated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("event_id"))
    op.create_index("ix_legacy_cluster_event_map_event_id", "legacy_cluster_event_map", ["event_id"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("industry", sa.String(), nullable=True),
        sa.Column("primary_region", sa.String(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("slug"))
    op.create_index("ix_customers_name", "customers", ["name"])
    op.create_index("ix_customers_slug", "customers", ["slug"])
    op.create_index("ix_customers_industry", "customers", ["industry"])
    op.create_index("ix_customers_primary_region", "customers", ["primary_region"])

    op.create_table(
        "watchlists",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("watchlist_type", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_watchlists_customer_id", "watchlists", ["customer_id"])
    op.create_index("ix_watchlists_watchlist_type", "watchlists", ["watchlist_type"])

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("watchlist_id", sa.String(length=36), sa.ForeignKey("watchlists.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("item_type", sa.String(), nullable=False),
        sa.Column("criticality_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_watchlist_items_watchlist_id", "watchlist_items", ["watchlist_id"])
    op.create_index("ix_watchlist_items_entity_id", "watchlist_items", ["entity_id"])
    op.create_index("ix_watchlist_items_item_type", "watchlist_items", ["item_type"])

    op.create_table(
        "exposure_links",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("source_object_type", sa.String(), nullable=False),
        sa.Column("source_object_id", sa.String(length=64), nullable=False),
        sa.Column("target_entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("relationship_type", sa.String(), nullable=False),
        sa.Column("criticality_score", sa.Float(), nullable=True),
        sa.Column("exposure_weight", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_exposure_links_customer_id", "exposure_links", ["customer_id"])
    op.create_index("ix_exposure_links_source_object_type", "exposure_links", ["source_object_type"])
    op.create_index("ix_exposure_links_source_object_id", "exposure_links", ["source_object_id"])
    op.create_index("ix_exposure_links_target_entity_id", "exposure_links", ["target_entity_id"])
    op.create_index("ix_exposure_links_relationship_type", "exposure_links", ["relationship_type"])


def downgrade() -> None:
    op.drop_index("ix_exposure_links_relationship_type", table_name="exposure_links")
    op.drop_index("ix_exposure_links_target_entity_id", table_name="exposure_links")
    op.drop_index("ix_exposure_links_source_object_id", table_name="exposure_links")
    op.drop_index("ix_exposure_links_source_object_type", table_name="exposure_links")
    op.drop_index("ix_exposure_links_customer_id", table_name="exposure_links")
    op.drop_table("exposure_links")

    op.drop_index("ix_watchlist_items_item_type", table_name="watchlist_items")
    op.drop_index("ix_watchlist_items_entity_id", table_name="watchlist_items")
    op.drop_index("ix_watchlist_items_watchlist_id", table_name="watchlist_items")
    op.drop_table("watchlist_items")

    op.drop_index("ix_watchlists_watchlist_type", table_name="watchlists")
    op.drop_index("ix_watchlists_customer_id", table_name="watchlists")
    op.drop_table("watchlists")

    op.drop_index("ix_customers_primary_region", table_name="customers")
    op.drop_index("ix_customers_industry", table_name="customers")
    op.drop_index("ix_customers_slug", table_name="customers")
    op.drop_index("ix_customers_name", table_name="customers")
    op.drop_table("customers")

    op.drop_index("ix_legacy_cluster_event_map_event_id", table_name="legacy_cluster_event_map")
    op.drop_table("legacy_cluster_event_map")

    op.drop_index("ix_event_entities_event_role", table_name="event_entities")
    op.drop_index("ix_event_entities_entity_id", table_name="event_entities")
    op.drop_index("ix_event_entities_event_id", table_name="event_entities")
    op.drop_table("event_entities")

    op.drop_index("ix_event_evidence_legacy_document_id", table_name="event_evidence")
    op.drop_index("ix_event_evidence_event_id", table_name="event_evidence")
    op.drop_table("event_evidence")

    op.drop_index("ix_events_last_seen_at", table_name="events")
    op.drop_index("ix_events_first_seen_at", table_name="events")
    op.drop_index("ix_events_status", table_name="events")
    op.drop_index("ix_events_canonical_title", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_entities_v2_canonical_name", table_name="entities_v2")
    op.drop_index("ix_entities_v2_entity_type", table_name="entities_v2")
    op.drop_index("ix_entities_v2_legacy_entity_id", table_name="entities_v2")
    op.drop_table("entities_v2")
