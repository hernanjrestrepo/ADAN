"""Structured logging configuration."""
import logging
import sys
import json
from datetime import datetime, timezone

from app.core.observability import request_id_var


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO"):
    """Configure structured logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with JSON format
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    return root_logger


def log_request(logger, request_id: str, method: str, path: str, status: int, duration: float):
    """Log an HTTP request."""
    logger.info(
        f"{method} {path} {status}",
        extra={"extra_data": {
            "request_id": request_id,
            "method": method,
            "path": path,
            "status": status,
            "duration_s": round(duration, 3),
        }}
    )


def log_ai_call(logger, operation: str, model: str, duration: float, tokens: int = 0):
    """Log an AI inference call."""
    logger.info(
        f"AI {operation}",
        extra={"extra_data": {
            "operation": operation,
            "model": model,
            "duration_s": round(duration, 3),
            "tokens": tokens,
        }}
    )
