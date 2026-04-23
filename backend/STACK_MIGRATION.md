# GeoSyn Stack Migration

GeoSyn has been reshaped toward the target production stack:

- FastAPI
- PostgreSQL
- Redis + Celery
- Object Storage
- Prometheus + Grafana
- OpenTelemetry

## What Changed

### API runtime

- `app/main.py` no longer runs the in-process infinite polling loop.
- FastAPI is now the API surface only.
- Prometheus metrics and OpenTelemetry bootstrap are initialized at startup.

### Database

- `app/core/config.py` now defaults to PostgreSQL-style connection settings.
- `app/db/session.py` uses connection pooling for PostgreSQL.
- `migrate_db.py` now assumes JSON-capable SQL backends rather than SQLite-only text fields.

### Background jobs

- `app/core/celery_app.py` defines the Celery broker/backend and beat schedule.
- `app/workers/tasks.py` moves the old polling responsibilities into worker tasks:
  - `run_high_frequency_sync`
  - `run_anchor_sync`

### Object storage

- `app/utils/datalake_manager.py` now supports:
  - local filesystem storage
  - S3-compatible object storage such as MinIO

### Operations

- `GET /api/v1/ops/health`
- `GET /api/v1/ops/ready`
- `GET /api/v1/ops/tasks/{task_id}`

### Queue-aware runtime endpoints

Operational endpoints now support queue-backed execution with `enqueue=true`:

- `POST /api/v1/ingestion/trigger?enqueue=true`
- `POST /api/v1/ingestion/compliance?enqueue=true`
- `POST /api/v1/clustering/trigger?enqueue=true`
- `POST /api/v1/markets/sync?enqueue=true`
- `POST /api/v1/nexus/sync?enqueue=true`
- `POST /api/v1/alerts/v2/generate?enqueue=true`

This preserves synchronous compatibility for the current frontend while allowing the
new Redis + Celery runtime to own heavier operational work.

## Local Startup

1. Create env file:

```bash
cp backend/.env.example backend/.env
```

2. Start the full stack:

```bash
docker compose up -d --build
```

3. The backend container applies Alembic migrations and seeds deterministic demo
   data on startup. Local entrypoints after boot:

- Frontend: `http://localhost:3002`
- API: `http://localhost:8000`
- Grafana: `http://localhost:3001`
- Prometheus: `http://localhost:9090`
- MinIO Console: `http://localhost:9001`

4. Verify the stack:

```bash
docker compose ps
docker compose logs -f backend
```

## Remaining Follow-Through

This migration now includes the main runtime pieces, but a few follow-up areas still matter:

- remove remaining SQLite-specific assumptions in scripts and docs
- add Redis caching where useful, not just Celery transport
- emit custom business metrics for ingestion, clustering, alerts, and exposure matching
- connect OTLP to a durable tracing backend in deployment
- add bucket bootstrap/retention policy for object storage
