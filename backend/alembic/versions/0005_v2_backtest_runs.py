"""v2 backtest runs

Revision ID: 0005_v2_backtest_runs
Revises: 0004_v2_event_timelines
Create Date: 2026-04-17 01:10:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "5_backtest"
down_revision = "4_timelines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "backtest_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_name", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("config", sa.Text(), nullable=True),
        sa.Column("metrics", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_backtest_runs_run_name", "backtest_runs", ["run_name"])
    op.create_index("ix_backtest_runs_customer_id", "backtest_runs", ["customer_id"])
    op.create_index("ix_backtest_runs_started_at", "backtest_runs", ["started_at"])
    op.create_index("ix_backtest_runs_completed_at", "backtest_runs", ["completed_at"])
    op.create_index("ix_backtest_runs_status", "backtest_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_backtest_runs_status", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_completed_at", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_started_at", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_customer_id", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_run_name", table_name="backtest_runs")
    op.drop_table("backtest_runs")
