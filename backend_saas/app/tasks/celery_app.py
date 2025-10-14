"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "ssl_monitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ssl_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.periodic_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.ssl_tasks.*": {"queue": "ssl_checks"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
        "app.tasks.periodic_tasks.*": {"queue": "periodic"},
    },
    
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task result settings
    result_expires=3600,  # 1 hour
    result_backend_max_retries=3,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "check-all-ssl-certificates": {
            "task": "app.tasks.periodic_tasks.check_all_ssl_certificates",
            "schedule": settings.SSL_CHECK_INTERVAL,  # seconds
        },
        "send-weekly-reports": {
            "task": "app.tasks.periodic_tasks.send_weekly_reports",
            "schedule": 7 * 24 * 60 * 60,  # 7 days in seconds
        },
        "cleanup-old-check-results": {
            "task": "app.tasks.periodic_tasks.cleanup_old_check_results",
            "schedule": 24 * 60 * 60,  # 24 hours in seconds
        },
        "sync-calendly-events": {
            "task": "app.tasks.periodic_tasks.sync_calendly_events",
            "schedule": 30 * 60,  # 30 minutes in seconds
        },
    },
)

# Task error handling
celery_app.conf.task_annotations = {
    "*": {"rate_limit": "10/s"},
    "app.tasks.ssl_tasks.check_ssl_certificate": {"rate_limit": "5/s"},
}

# Health check
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f"Request: {self.request!r}")
    return "Celery is working!"
