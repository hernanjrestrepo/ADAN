"""Structured logging configuration (JSON, con request_id de la request en curso)."""
import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record):
        from app.core.observability import current_request_id

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = current_request_id()
        if request_id:
            log_entry["request_id"] = request_id
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False, default=str)


def setup_logging(level: str = "INFO"):
    """Configure structured logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with JSON format
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Evitar el access log duplicado de uvicorn (lo emite RequestContextMiddleware)
    logging.getLogger("uvicorn.access").disabled = True

    return root_logger


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
