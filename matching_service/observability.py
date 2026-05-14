"""Наблюдаемость: JSON-логи, Correlation ID, Prometheus /metrics, Sentry (опционально)."""
from __future__ import annotations

import contextvars
import json
import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

HEADER_CORRELATION_ID = "X-Correlation-ID"

correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str | None:
    return correlation_id_var.get()


class _CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        cid = correlation_id_var.get()
        record.correlation_id = cid if cid else "-"
        return True


class _JsonFormatter(logging.Formatter):
    def __init__(self, service_name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self._service_name,
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _configure_logging(service_name: str) -> None:
    use_json = os.getenv("LOG_JSON", "true").lower() in ("1", "true", "yes")
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    filt = _CorrelationIdFilter()
    root = logging.getLogger()
    root.handlers.clear()
    root.addFilter(filt)
    root.setLevel(level)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.addFilter(filt)
    if use_json:
        stdout_handler.setFormatter(_JsonFormatter(service_name))
    else:
        stdout_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s"
            )
        )
    root.addHandler(stdout_handler)

    # Файл: одна строка = один JSON-объект (NDJSON). Путь задаётся LOG_FILE.
    log_file = os.getenv("LOG_FILE", "").strip()
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        max_bytes = int(os.getenv("LOG_FILE_MAX_BYTES", str(10 * 1024 * 1024)))
        backup = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup,
            encoding="utf-8",
        )
        file_handler.addFilter(filt)
        file_handler.setFormatter(_JsonFormatter(service_name))
        root.addHandler(file_handler)


def _init_sentry(service_name: str) -> None:
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        return
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", os.getenv("ENVIRONMENT", "development")),
        release=os.getenv("SENTRY_RELEASE", "") or None,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        send_default_pii=False,
    )
    sentry_sdk.set_tag("service", service_name)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Принимает или генерирует X-Correlation-ID; доступен в логах и request.state."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        raw = request.headers.get("x-correlation-id")
        cid = raw.strip() if raw else str(uuid.uuid4())
        token = correlation_id_var.set(cid)
        request.state.correlation_id = cid
        try:
            response = await call_next(request)
        finally:
            correlation_id_var.reset(token)
        response.headers[HEADER_CORRELATION_ID] = cid
        return response


def _setup_prometheus(app: FastAPI) -> None:
    if os.getenv("PROMETHEUS_ENABLED", "true").lower() not in ("1", "true", "yes"):
        return
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def setup_observability(app: FastAPI, service_name: str) -> None:
    """Вызывать после include_router (чтобы /metrics был зарегистрирован)."""
    _configure_logging(service_name)
    _init_sentry(service_name)
    app.add_middleware(CorrelationIdMiddleware)
    _setup_prometheus(app)
    logging.getLogger(__name__).info("observability enabled service=%s", service_name)
