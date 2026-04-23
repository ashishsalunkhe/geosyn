"""v2 alerts and exposure

Revision ID: 0002_v2_alerts_and_exposure
Revises: 0001_v2_foundation
Create Date: 2026-04-17 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "2_alerts"
down_revision = "1_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("supplier_name", sa.String(), nullable=False),
        sa.Column("tier_level", sa.Integer(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("criticality_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_suppliers_customer_id", "suppliers", ["customer_id"])
    op.create_index("ix_suppliers_entity_id", "suppliers", ["entity_id"])
    op.create_index("ix_suppliers_supplier_name", "suppliers", ["supplier_name"])
    op.create_index("ix_suppliers_country_code", "suppliers", ["country_code"])

    op.create_table(
        "facilities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("facility_name", sa.String(), nullable=False),
        sa.Column("facility_type", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("criticality_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_facilities_customer_id", "facilities", ["customer_id"])
    op.create_index("ix_facilities_entity_id", "facilities", ["entity_id"])
    op.create_index("ix_facilities_facility_name", "facilities", ["facility_name"])
    op.create_index("ix_facilities_facility_type", "facilities", ["facility_type"])
    op.create_index("ix_facilities_country_code", "facilities", ["country_code"])

    op.create_table(
        "alerts_v2",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("alert_type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("headline", sa.String(), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("triggered_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_alerts_v2_customer_id", "alerts_v2", ["customer_id"])
    op.create_index("ix_alerts_v2_event_id", "alerts_v2", ["event_id"])
    op.create_index("ix_alerts_v2_alert_type", "alerts_v2", ["alert_type"])
    op.create_index("ix_alerts_v2_severity", "alerts_v2", ["severity"])
    op.create_index("ix_alerts_v2_status", "alerts_v2", ["status"])
    op.create_index("ix_alerts_v2_triggered_at", "alerts_v2", ["triggered_at"])

    op.create_table(
        "alert_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.String(length=36), sa.ForeignKey("alerts_v2.id"), nullable=False),
        sa.Column("legacy_document_id", sa.Integer(), nullable=False),
        sa.Column("evidence_type", sa.String(), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_alert_evidence_alert_id", "alert_evidence", ["alert_id"])
    op.create_index("ix_alert_evidence_legacy_document_id", "alert_evidence", ["legacy_document_id"])

    op.create_table(
        "alert_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.String(length=36), sa.ForeignKey("alerts_v2.id"), nullable=False),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_alert_actions_alert_id", "alert_actions", ["alert_id"])
    op.create_index("ix_alert_actions_action_type", "alert_actions", ["action_type"])


def downgrade() -> None:
    op.drop_index("ix_alert_actions_action_type", table_name="alert_actions")
    op.drop_index("ix_alert_actions_alert_id", table_name="alert_actions")
    op.drop_table("alert_actions")

    op.drop_index("ix_alert_evidence_legacy_document_id", table_name="alert_evidence")
    op.drop_index("ix_alert_evidence_alert_id", table_name="alert_evidence")
    op.drop_table("alert_evidence")

    op.drop_index("ix_alerts_v2_triggered_at", table_name="alerts_v2")
    op.drop_index("ix_alerts_v2_status", table_name="alerts_v2")
    op.drop_index("ix_alerts_v2_severity", table_name="alerts_v2")
    op.drop_index("ix_alerts_v2_alert_type", table_name="alerts_v2")
    op.drop_index("ix_alerts_v2_event_id", table_name="alerts_v2")
    op.drop_index("ix_alerts_v2_customer_id", table_name="alerts_v2")
    op.drop_table("alerts_v2")

    op.drop_index("ix_facilities_country_code", table_name="facilities")
    op.drop_index("ix_facilities_facility_type", table_name="facilities")
    op.drop_index("ix_facilities_facility_name", table_name="facilities")
    op.drop_index("ix_facilities_entity_id", table_name="facilities")
    op.drop_index("ix_facilities_customer_id", table_name="facilities")
    op.drop_table("facilities")

    op.drop_index("ix_suppliers_country_code", table_name="suppliers")
    op.drop_index("ix_suppliers_supplier_name", table_name="suppliers")
    op.drop_index("ix_suppliers_entity_id", table_name="suppliers")
    op.drop_index("ix_suppliers_customer_id", table_name="suppliers")
    op.drop_table("suppliers")
