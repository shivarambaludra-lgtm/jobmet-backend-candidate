from functools import wraps
import time
from app.utils.logger import logger
from typing import Callable
import asyncio

def log_slow_queries(threshold_ms: float = 1000):
    """Decorator to log slow database queries"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                logger.warning(
                    f"Slow query detected: {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                        "threshold_ms": threshold_ms
                    }
                )
            
            return result
        return wrapper
    return decorator

def measure_time(operation_name: str = "operation"):
    """Decorator to measure execution time"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Performance: {operation_name}",
                extra={
                    "operation": operation_name,
                    "duration_ms": round(duration_ms, 2)
                }
            )
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Performance: {operation_name}",
                extra={
                    "operation": operation_name,
                    "duration_ms": round(duration_ms, 2)
                }
            )
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class PerformanceMonitor:
    """Context manager for performance monitoring"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        logger.info(
            f"Performance: {self.operation_name}",
            extra={
                "operation": self.operation_name,
                "duration_ms": round(duration_ms, 2),
                "success": exc_type is None
            }
        )
