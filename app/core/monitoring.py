import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from app.core.config import settings
from typing import Optional, Dict, Any

def init_sentry():
    """Initialize Sentry error tracking and performance monitoring"""
    
    if not settings.SENTRY_DSN:
        print("⚠️  Sentry DSN not configured, skipping initialization")
        return
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(transaction_style="url"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration()
        ],
        send_default_pii=False,
        attach_stacktrace=True,
        before_send=filter_sensitive_data
    )
    
    print("✓ Sentry initialized")

def filter_sensitive_data(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Remove sensitive data from Sentry events"""
    
    if "request" in event:
        if "data" in event["request"]:
            data = event["request"]["data"]
            if isinstance(data, dict):
                data.pop("password", None)
                data.pop("api_key", None)
                data.pop("token", None)
        
        if "headers" in event["request"]:
            headers = event["request"]["headers"]
            if isinstance(headers, dict):
                headers.pop("Authorization", None)
                headers.pop("Cookie", None)
    
    return event
