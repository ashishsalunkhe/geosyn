"""
Database migration helper for the GeoSyn Postgres stack.

Recommended:
    alembic upgrade head

Compatibility fallback:
    python migrate_db.py
"""
import os
import sys

import sqlalchemy as sa

sys.path.insert(0, os.path.dirname(__file__))

from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402


def column_exists(inspector, table_name: str, column_name: str) -> bool:
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def migrate():
    Base.metadata.create_all(bind=engine)
    print("[migrate] create_all() complete.")

    inspector = sa.inspect(engine)

    if column_exists(inspector, "alerts", "alert_payload"):
        print("[migrate] alerts.alert_payload already present.")
    elif "alerts" in inspector.get_table_names():
        with engine.begin() as connection:
            connection.execute(sa.text("ALTER TABLE alerts ADD COLUMN alert_payload JSON"))
        print("[migrate] Added alerts.alert_payload")

    if column_exists(inspector, "causal_nodes", "node_meta"):
        print("[migrate] causal_nodes.node_meta already present.")
    elif "causal_nodes" in inspector.get_table_names():
        with engine.begin() as connection:
            connection.execute(sa.text("ALTER TABLE causal_nodes ADD COLUMN node_meta JSON"))
        print("[migrate] Added causal_nodes.node_meta")

    print("[migrate] Migration complete.")


if __name__ == "__main__":
    migrate()
