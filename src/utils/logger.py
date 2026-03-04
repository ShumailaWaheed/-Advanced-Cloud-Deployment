"""Logging utilities for the todo chatbot application."""

import logging
import sys
from typing import Optional
import json
from datetime import datetime


class CorrelationIdFilter(logging.Filter):
    """Logging filter to add correlation ID to log records."""

    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__()
        self.correlation_id = correlation_id

    def filter(self, record):
        record.correlation_id = getattr(record, 'correlation_id', self.correlation_id or 'N/A')
        return True


def setup_logger(
    name: str,
    level: int = logging.INFO,
    correlation_id: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up a structured logger with correlation ID support.

    Args:
        name: Logger name
        level: Logging level
        correlation_id: Optional correlation ID for distributed tracing
        log_format: Optional custom log format

    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[Correlation-ID: %(correlation_id)s] - %(message)s'
        )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Add correlation ID filter
    correlation_filter = CorrelationIdFilter(correlation_id)
    handler.addFilter(correlation_filter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


def log_structured(
    logger: logging.Logger,
    level: int,
    message: str,
    correlation_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log a structured message with additional context.

    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        correlation_id: Optional correlation ID
        **kwargs: Additional context fields
    """
    context = {
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'context': kwargs
    }

    if correlation_id:
        context['correlation_id'] = correlation_id

    logger.log(level, json.dumps(context))


def get_correlation_id_from_context() -> Optional[str]:
    """
    Get correlation ID from current execution context.
    This is a simplified version - in a real implementation,
    this would integrate with request context managers.
    """
    # Placeholder implementation
    return None