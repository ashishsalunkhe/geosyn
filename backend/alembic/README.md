# Alembic Setup

Run from `backend/`:

```bash
alembic revision -m "message"
alembic upgrade head
```

The environment is configured to use `app.db.base.Base.metadata` as the migration target.

Expected local runtime:

- PostgreSQL for the primary relational store
- Redis for Celery broker and result backend

Typical setup:

```bash
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
```
