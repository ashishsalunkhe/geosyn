"""v2 event timelines

Revision ID: 0004_v2_event_timelines
Revises: 0003_v2_graph_risk_and_provenance
Create Date: 2026-04-17 00:50:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "4_timelines"
down_revision = "3_graph"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_timelines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_document_id", sa.String(length=36), sa.ForeignKey("evidence_documents.id"), nullable=True),
        sa.Column("timeline_type", sa.String(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_event_timelines_event_id", "event_timelines", ["event_id"])
    op.create_index("ix_event_timelines_occurred_at", "event_timelines", ["occurred_at"])
    op.create_index("ix_event_timelines_source_document_id", "event_timelines", ["source_document_id"])
    op.create_index("ix_event_timelines_timeline_type", "event_timelines", ["timeline_type"])


def downgrade() -> None:
    op.drop_index("ix_event_timelines_timeline_type", table_name="event_timelines")
    op.drop_index("ix_event_timelines_source_document_id", table_name="event_timelines")
    op.drop_index("ix_event_timelines_occurred_at", table_name="event_timelines")
    op.drop_index("ix_event_timelines_event_id", table_name="event_timelines")
    op.drop_table("event_timelines")
