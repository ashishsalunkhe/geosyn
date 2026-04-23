#!/bin/sh
set -e

echo "GeoSyn: waiting for postgres DNS and port..."
python - <<'PY'
import os
import socket
import sys
import time

host = os.getenv("POSTGRES_SERVER", "postgres")
port = int(os.getenv("POSTGRES_PORT", "5432"))

deadline = time.time() + 90
last_error = None

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"GeoSyn: postgres is reachable at {host}:{port}")
            sys.exit(0)
    except OSError as exc:
        last_error = exc
        time.sleep(2)

print(f"GeoSyn: postgres did not become reachable at {host}:{port}: {last_error}", file=sys.stderr)
sys.exit(1)
PY

echo "GeoSyn: applying database migrations..."
python -m alembic upgrade head

if [ "${DEMO_SEED_ENABLED:-true}" = "true" ]; then
  echo "GeoSyn: seeding demo runtime data..."
  python scripts/seed_demo_runtime.py
fi

echo "GeoSyn: starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
