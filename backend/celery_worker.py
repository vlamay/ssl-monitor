from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from datetime import datetime
import os
import sys
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from services import ssl_service
from services.telegram_bot import send_telegram_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery('ssl_monitor', broker=REDIS_URL, backend=REDIS_URL)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)

# Beat schedule configuration
celery_app.conf.beat_schedule = {
    'check-all-domains-hourly': {
        'task': 'celery_worker.check_all_domains',
        'schedule': crontab(minute=0, hour='*'),  # Every hour
    },
    'cleanup-old-checks': {
        'task': 'celery_worker.cleanup_old_checks',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

@celery_app.task(name='celery_worker.check_domain_ssl')
def check_domain_ssl(domain_id: int, domain_name: str):
    """
    Check SSL certificate for a single domain (Celery task)
    
    Args:
        domain_id: Database ID of the domain
        domain_name: Domain name to check
    """
    logger.info(f"Starting SSL check for domain: {domain_name} (ID: {domain_id})")
    
    db = SessionLocal()
    try:
        # Get domain from database
        domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
        if not domain or not domain.is_active:
            logger.warning(f"Domain {domain_name} not found or inactive")
            return
        
        # Perform SSL check
        result = ssl_service.check_ssl_certificate(domain_name)
        
        # Save check result to database
        ssl_check = models.SSLCheck(
            domain_id=domain_id,
            expires_in=result.get("expires_in"),
            is_valid=result.get("is_valid", False),
            error_message=result.get("error"),
            issuer=result.get("issuer"),
            subject=result.get("subject"),
            not_valid_before=result.get("not_valid_before"),
            not_valid_after=result.get("not_valid_after")
        )
        
        db.add(ssl_check)
        db.commit()
        
        logger.info(f"SSL check saved for {domain_name}: valid={result.get('is_valid')}, expires_in={result.get('expires_in')}")
        
        # Check if alert should be sent
        if result.get("is_valid"):
            expires_in = result.get("expires_in", 0)
            if expires_in <= domain.alert_threshold_days:
                send_alert(domain_name, expires_in, "expiring")
        else:
            send_alert(domain_name, 0, "error", result.get("error"))
        
        return {
            "domain": domain_name,
            "status": "success",
            "is_valid": result.get("is_valid"),
            "expires_in": result.get("expires_in")
        }
        
    except Exception as e:
        logger.error(f"Error checking domain {domain_name}: {str(e)}")
        return {
            "domain": domain_name,
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

@celery_app.task(name='celery_worker.check_all_domains')
def check_all_domains():
    """
    Check SSL certificates for all active domains (Celery task)
    """
    logger.info("Starting SSL check for all active domains")
    
    db = SessionLocal()
    try:
        # Get all active domains
        domains = db.query(models.Domain).filter(models.Domain.is_active == True).all()
        
        logger.info(f"Found {len(domains)} active domains to check")
        
        # Schedule SSL check for each domain
        results = []
        for domain in domains:
            result = check_domain_ssl.delay(domain.id, domain.name)
            results.append({
                "domain": domain.name,
                "task_id": result.id
            })
        
        return {
            "status": "scheduled",
            "domains_count": len(domains),
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Error scheduling domain checks: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

@celery_app.task(name='celery_worker.cleanup_old_checks')
def cleanup_old_checks(days_to_keep: int = 90):
    """
    Clean up old SSL check records (Celery task)
    
    Args:
        days_to_keep: Number of days of history to keep (default: 90)
    """
    logger.info(f"Starting cleanup of SSL checks older than {days_to_keep} days")
    
    db = SessionLocal()
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old checks
        deleted_count = db.query(models.SSLCheck)\
            .filter(models.SSLCheck.checked_at < cutoff_date)\
            .delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old SSL check records")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        db.rollback()
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

def send_alert(domain: str, days_left: int, alert_type: str = "expiring", error_msg: str = None):
    """
    Send alert notifications for SSL certificate issues
    
    Args:
        domain: Domain name
        days_left: Days until expiration
        alert_type: Type of alert ("expiring", "error")
        error_msg: Error message (for error alerts)
    """
    try:
        if alert_type == "expiring":
            if days_left <= 0:
                message = f"🚨 CRITICAL: SSL certificate for {domain} has EXPIRED!"
                logger.critical(message)
            elif days_left <= 7:
                message = f"⚠️ URGENT: SSL certificate for {domain} expires in {days_left} days!"
                logger.warning(message)
            elif days_left <= 30:
                message = f"⚠️ WARNING: SSL certificate for {domain} expires in {days_left} days"
                logger.warning(message)
            else:
                return  # No alert needed
        else:  # error
            message = f"❌ ERROR: SSL check failed for {domain}"
            if error_msg:
                message += f"\nError: {error_msg}"
            logger.error(message)
        
        # Send to Telegram (if configured)
        send_telegram_alert(message)
        
        # Here you can add other notification channels:
        # - Email
        # - Slack
        # - Discord
        # - PagerDuty
        # etc.
        
    except Exception as e:
        logger.error(f"Error sending alert for {domain}: {str(e)}")

if __name__ == '__main__':
    # Run worker with: celery -A celery_worker worker --loglevel=info
    # Run beat with: celery -A celery_worker beat --loglevel=info
    celery_app.start()

