from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.core.telemetry import setup_prometheus, setup_telemetry
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_prometheus(app)
setup_telemetry(app, engine)


@app.get("/")
def root():
    return {
        "message": "Welcome to GeoSyn API",
        "environment": settings.ENVIRONMENT,
        "stack": {
            "api": "FastAPI",
            "database": "PostgreSQL",
            "queue": "Redis + Celery",
            "storage": settings.OBJECT_STORAGE_PROVIDER,
            "metrics": "Prometheus",
            "tracing": "OpenTelemetry" if settings.OTEL_ENABLED else "disabled",
        },
    }


app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
