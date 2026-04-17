# Alembic Setup

Run from `backend/`:

```bash
alembic revision -m "message"
alembic upgrade head
```

The environment is configured to use `app.db.base.Base.metadata` as the migration target.
