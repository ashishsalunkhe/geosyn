from fastapi import APIRouter
from sqlalchemy import text
from celery.result import AsyncResult
import redis

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import engine


router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database": settings.get_db_url().split("://", 1)[0],
        "redis": settings.get_redis_url(),
        "object_storage": settings.OBJECT_STORAGE_PROVIDER,
    }


@router.get("/ready")
def readiness_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    client = redis.Redis.from_url(settings.get_redis_url())
    client.ping()
    return {"status": "ready"}


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    payload = {
        "task_id": task_id,
        "status": result.status,
    }
    if result.successful():
        payload["result"] = result.result
    elif result.failed():
        payload["error"] = str(result.result)
    return payload
