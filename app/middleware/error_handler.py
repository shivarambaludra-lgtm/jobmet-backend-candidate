from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import logger
from app.core.monitoring import capture_exception
from sqlalchemy.exc import SQLAlchemyError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors()
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    
    logger.warning(
        "HTTP exception",
        extra={
            "path": request.url.path,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    
    logger.error(
        "Database error",
        extra={
            "path": request.url.path,
            "error": str(exc)
        },
        exc_info=True
    )
    
    if hasattr(capture_exception, '__call__'):
        capture_exception(exc, context={"path": request.url.path})
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "message": "An error occurred while processing your request"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    
    logger.error(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "error": str(exc),
            "error_type": type(exc).__name__
        },
        exc_info=True
    )
    
    if hasattr(capture_exception, '__call__'):
        capture_exception(exc, context={
            "path": request.url.path,
            "method": request.method
        })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )
