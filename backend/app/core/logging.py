"""
Structured Logging Configuration
"""
import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime
from typing import Any, Dict
import structlog

from app.core.config import settings


class AuditLogger:
    """Audit logging for tracking user actions and system events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_action(
        self,
        action: str,
        resource: str,
        resource_id: str = None,
        user_id: str = None,
        details: Dict[str, Any] = None,
        status: str = "success"
    ):
        """Log an auditable action"""
        self.logger.info(
            "audit_event",
            action=action,
            resource=resource,
            resource_id=resource_id,
            user_id=user_id,
            details=details or {},
            status=status,
            timestamp=datetime.utcnow().isoformat()
        )


def setup_logging():
    """Setup structured logging for the application"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    log_handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT == "json":
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        log_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        handlers=[log_handler]
    )


# Global logger instance
logger = structlog.get_logger()

# Global audit logger instance
audit_logger = AuditLogger()
