from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.saved_search import SavedSearch
from app.models.user import User
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Dict, Any

@celery_app.task(name="app.tasks.email_tasks.send_saved_search_alerts")
def send_saved_search_alerts() -> Dict[str, Any]:
    """Send email alerts for saved searches with new jobs"""
    
    db = SessionLocal()
    
    try:
        now = datetime.utcnow()
        
        saved_searches = db.query(SavedSearch).filter(
            SavedSearch.email_alerts == True,
            SavedSearch.is_active == True
        ).all()
        
        sent_count = 0
        errors = []
        
        for search in saved_searches:
            if search.last_run_at:
                hours_since_last = (now - search.last_run_at).total_seconds() / 3600
                
                if search.alert_frequency == "daily" and hours_since_last < 24:
                    continue
                elif search.alert_frequency == "weekly" and hours_since_last < 168:
                    continue
            
            user = db.query(User).filter(User.id == search.user_id).first()
            if not user or not user.email:
                continue
            
            try:
                send_email(
                    to_email=user.email,
                    subject=f"New jobs for: {search.name}",
                    body=_generate_email_body(user, search)
                )
                
                search.last_run_at = now
                sent_count += 1
            
            except Exception as e:
                errors.append(f"Error sending to {user.email}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "success",
            "sent": sent_count,
            "errors": errors
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

def send_email(to_email: str, subject: str, body: str):
    """Send email via SMTP"""
    
    msg = MIMEMultipart("alternative")
    msg['From'] = settings.SMTP_FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    
    text_part = MIMEText(body, 'plain')
    msg.attach(text_part)
    
    html_body = body.replace('\n', '<br>')
    html_part = MIMEText(f"<html><body>{html_body}</body></html>", 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)

def _generate_email_body(user: User, search: SavedSearch) -> str:
    """Generate email body for saved search alert"""
    
    return f"""
Hi {user.full_name or 'there'},

We found {search.new_jobs_count or 0} new jobs matching your saved search "{search.name}".

Query: {search.query}

View your results here:
https://jobmet.ai/search/{search.id}

Best regards,
JobMet Team
"""
