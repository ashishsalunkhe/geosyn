from __future__ import annotations

import logging

from fastapi import FastAPI

from app.core.config import settings


logger = logging.getLogger(__name__)


def setup_prometheus(app: FastAPI) -> None:
    if not settings.PROMETHEUS_ENABLED:
        return
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, include_in_schema=False, tags=["ops"])
    except Exception as exc:
        logger.warning("Prometheus instrumentation unavailable: %s", exc)


def setup_telemetry(app: FastAPI, engine) -> None:
    if not settings.OTEL_ENABLED:
        return
    if not settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        logger.warning("OTEL is enabled but OTLP endpoint is not configured")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            headers=settings.OTEL_EXPORTER_OTLP_HEADERS,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument(engine=engine)
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
    except Exception as exc:
        logger.warning("OpenTelemetry instrumentation unavailable: %s", exc)
