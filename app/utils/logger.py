import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        log_record['environment'] = settings.ENVIRONMENT
        log_record['service'] = 'jobmet-backend'
        
        if 'levelname' in log_record:
            log_record['level'] = log_record['levelname']

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging"""
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level))
    logger.handlers = []
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    formatter = CustomJsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger

logger = setup_logging(level=settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO")
