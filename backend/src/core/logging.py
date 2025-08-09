"""
Logging configuration using Loguru.
Provides structured logging with proper formatting and log levels.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

from loguru import logger

from config.settings import settings


def serialize_log_record(record: Dict[str, Any]) -> str:
    """Serialize log record to JSON format."""
    
    # Extract relevant fields
    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Add extra fields if present
    if "extra" in record and record["extra"]:
        log_data["extra"] = record["extra"]
    
    # Add exception info if present
    if record["exception"]:
        log_data["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
            "traceback": record["exception"].traceback,
        }
    
    return json.dumps(log_data, default=str)


def format_log_record(record: Dict[str, Any]) -> str:
    """Format log record for human-readable output."""
    
    timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    level = record["level"].name.ljust(8)
    module = record["name"]
    function = record["function"]
    line = record["line"]
    message = record["message"]
    
    # Basic format
    log_line = f"{timestamp} | {level} | {module}:{function}:{line} - {message}"
    
    # Add extra fields if present
    if "extra" in record and record["extra"]:
        extra_str = " | ".join(f"{k}={v}" for k, v in record["extra"].items())
        log_line += f" | {extra_str}"
    
    return log_line


def setup_logging() -> None:
    """Configure logging with Loguru."""
    
    # Remove default logger
    logger.remove()
    
    # Console logging
    if settings.is_development:
        # Human-readable format for development
        logger.add(
            sys.stdout,
            format=format_log_record,
            level=settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # JSON format for production
        logger.add(
            sys.stdout,
            format=serialize_log_record,
            level=settings.log_level,
            serialize=False,  # We handle serialization manually
            backtrace=False,
            diagnose=False,
        )
    
    # File logging (always JSON format)
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Application logs
    logger.add(
        log_dir / "app.log",
        format=serialize_log_record,
        level="INFO",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        serialize=False,
        backtrace=True,
        diagnose=True,
    )
    
    # Error logs
    logger.add(
        log_dir / "error.log",
        format=serialize_log_record,
        level="ERROR",
        rotation="1 week",
        retention="8 weeks",
        compression="gz",
        serialize=False,
        backtrace=True,
        diagnose=True,
    )
    
    # Add request ID to all logs if available
    def add_request_id(record):
        # Try to get request ID from context
        try:
            import contextvars
            request_id = getattr(contextvars.copy_context(), 'request_id', None)
            if request_id:
                record["extra"]["request_id"] = request_id
        except:
            pass
        return record
    
    logger.configure(patcher=add_request_id)
    
    # Log configuration
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.log_level,
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )


def get_logger(name: str = __name__):
    """Get logger with specific name."""
    return logger.bind(name=name)


# Custom logging methods for common use cases
def log_request(method: str, path: str, status_code: int, duration: float) -> None:
    """Log HTTP request details."""
    logger.info(
        f"{method} {path}",
        extra={
            "event_type": "http_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )


def log_ai_request(
    model_name: str,
    prompt_length: int,
    response_length: int,
    duration: float,
    tokens_used: int = None,
) -> None:
    """Log AI model request details."""
    extra_data = {
        "event_type": "ai_request",
        "model_name": model_name,
        "prompt_length": prompt_length,
        "response_length": response_length,
        "duration_ms": round(duration * 1000, 2),
    }
    
    if tokens_used:
        extra_data["tokens_used"] = tokens_used
    
    logger.info(f"AI request to {model_name}", extra=extra_data)


def log_vector_search(
    query_length: int,
    results_count: int,
    duration: float,
    vector_store: str,
) -> None:
    """Log vector search details."""
    logger.info(
        f"Vector search in {vector_store}",
        extra={
            "event_type": "vector_search",
            "query_length": query_length,
            "results_count": results_count,
            "duration_ms": round(duration * 1000, 2),
            "vector_store": vector_store,
        },
    )


def log_document_processing(
    file_name: str,
    file_size: int,
    chunks_created: int,
    duration: float,
    success: bool = True,
) -> None:
    """Log document processing details."""
    level = "info" if success else "error"
    message = f"Document processed: {file_name}" if success else f"Document processing failed: {file_name}"
    
    getattr(logger, level)(
        message,
        extra={
            "event_type": "document_processing",
            "file_name": file_name,
            "file_size": file_size,
            "chunks_created": chunks_created,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
        },
    )


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""
    
    @property
    def logger(self):
        """Get logger for this class."""
        return logger.bind(class_name=self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with class context."""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with class context."""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message with class context."""
        self.logger.error(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with class context."""
        self.logger.debug(message, extra=kwargs)
