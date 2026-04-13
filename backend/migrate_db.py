"""
One-shot migration script: creates all tables (or adds missing columns)
so that geosyn.db matches the current SQLAlchemy models.

Run from backend/:
    python migrate_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.base import Base  # noqa – triggers model registration via wildcard import
from app.db.session import engine
import sqlalchemy as sa


def migrate():
    # ---------- 1. Create any tables that don't exist yet ----------
    Base.metadata.create_all(bind=engine)
    print("[migrate] create_all() complete – all defined tables now exist.")

    # ---------- 2. Add missing columns to existing tables ----------
    inspector = sa.inspect(engine)

    # -- alerts.alert_payload (JSON / TEXT in SQLite) --
    alerts_cols = {c["name"] for c in inspector.get_columns("alerts")}
    if "alert_payload" not in alerts_cols:
        with engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE alerts ADD COLUMN alert_payload TEXT"))
            conn.commit()
        print("[migrate] Added missing column: alerts.alert_payload")
    else:
        print("[migrate] alerts.alert_payload already present – skipping.")

    # -- causal_nodes.node_meta (JSON / TEXT in SQLite) --
    if "causal_nodes" in inspector.get_table_names():
        cn_cols = {c["name"] for c in inspector.get_columns("causal_nodes")}
        if "node_meta" not in cn_cols:
            with engine.connect() as conn:
                conn.execute(sa.text("ALTER TABLE causal_nodes ADD COLUMN node_meta TEXT"))
                conn.commit()
            print("[migrate] Added missing column: causal_nodes.node_meta")
        else:
            print("[migrate] causal_nodes.node_meta already present – skipping.")

    print("[migrate] Migration complete.")


if __name__ == "__main__":
    migrate()
