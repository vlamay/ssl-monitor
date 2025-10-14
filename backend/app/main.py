from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import sys
import os
import logging
import time

# Sentry integration
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    
    # Initialize Sentry if DSN is provided
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "production"),
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% for profiling
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
        )
        logging.info("✅ Sentry initialized for error tracking")
    else:
        logging.info("ℹ️  Sentry DSN not provided, skipping error tracking setup")
except ImportError:
    logging.warning("⚠️  Sentry SDK not installed, skipping error tracking setup")
except Exception as e:
    logging.error(f"❌ Failed to initialize Sentry: {e}")

# Prometheus metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_ENABLED = True
except ImportError:
    PROMETHEUS_ENABLED = False
    logging.warning("⚠️  Prometheus instrumentator not installed, skipping metrics")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import schemas
from database import engine, get_db
from services import ssl_service
from app import billing
from app.user_profile import router as user_profile_router  # PostgreSQL version
from app.user_redis import router as user_redis_router  # NEW: Redis version (no migration needed!)
from app.notifications import router as notifications_router  # NEW: Notifications API
from app.trial import router as trial_router  # NEW: Trial API
from app.migrate import run_migrations  # Auto migration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SSL Certificate Monitor API",
    version="1.0.0",
    description="Professional SSL certificate monitoring service with i18n support"
)

# Add Prometheus metrics if available
if PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(app)
    logging.info("✅ Prometheus metrics enabled at /metrics")

# Add Sentry middleware for request tracking
@app.middleware("http")
async def sentry_middleware(request: Request, call_next):
    """Add Sentry context to requests"""
    start_time = time.time()
    
    # Add request ID for tracking
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    
    try:
        # Set Sentry context if available
        if 'sentry_sdk' in globals():
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("request_id", request_id)
                scope.set_tag("method", request.method)
                scope.set_tag("path", request.url.path)
                scope.set_user({"id": None})  # Will be set when auth is implemented
        
        response = await call_next(request)
        
        # Add performance tracking
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Capture exceptions in Sentry
        if 'sentry_sdk' in globals():
            sentry_sdk.capture_exception(e)
        raise

# Startup event - run migrations
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Starting SSL Monitor Pro API...")
    
    # Run database migrations
    logger.info("🔄 Running database migrations...")
    migration_success = run_migrations()
    
    if migration_success:
        logger.info("✅ Database migrations completed")
    else:
        logger.warning("⚠️  Migration check failed, but continuing startup")
    
    # Create other tables via SQLAlchemy
    logger.info("🔄 Creating SQLAlchemy tables...")
    models.Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Application started successfully")

# Include routers
app.include_router(billing.router)
# app.include_router(user_profile_router)  # PostgreSQL version (commented out - needs migration)
app.include_router(user_redis_router)  # Redis version (works immediately!)
app.include_router(notifications_router)  # Notifications API (works immediately!)
app.include_router(trial_router)  # Trial API (works immediately!)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cloudsre.xyz",
        "https://www.cloudsre.xyz",
        "https://status.cloudsre.xyz",
        "http://localhost:8080",
        "http://localhost:3000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "SSL Certificate Monitor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        import redis
        import os
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            r = redis.from_url(redis_url)
            r.ping()
            health_status["checks"]["redis"] = "connected"
        else:
            health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
    
    # Check Telegram
    try:
        from utils.telegram import test_telegram_connection
        telegram_result = test_telegram_connection()
        if telegram_result.get('ok'):
            bot_username = telegram_result.get('bot', {}).get('username', 'unknown')
            health_status["checks"]["telegram"] = f"connected (@{bot_username})"
        else:
            health_status["checks"]["telegram"] = "not_configured"
    except Exception as e:
        health_status["checks"]["telegram"] = "not_configured"
    
    # Check Stripe
    try:
        import stripe
        import os
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if stripe.api_key and stripe.api_key.startswith('sk_'):
            # Just check if key is present, don't make API call
            health_status["checks"]["stripe"] = "configured"
        else:
            health_status["checks"]["stripe"] = "not_configured"
    except Exception as e:
        health_status["checks"]["stripe"] = "not_configured"
    
    # Return appropriate status code
    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status

@app.get("/ready")
async def readiness_check():
    """
    Kubernetes/Docker readiness probe
    Checks if the application is ready to receive traffic
    """
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}

@app.get("/live")
async def liveness_check():
    """
    Kubernetes/Docker liveness probe
    Checks if the application is alive and should be restarted
    """
    return {"alive": True, "timestamp": datetime.utcnow().isoformat()}

@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint (if enabled)
    """
    if not PROMETHEUS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prometheus metrics not enabled"
        )
    
    # This will be handled by the Prometheus instrumentator
    # The endpoint is automatically exposed at /metrics
    return {"message": "Prometheus metrics available at /metrics"}

# Domain Endpoints
@app.post("/domains/", status_code=status.HTTP_201_CREATED)
def create_domain(domain: schemas.DomainCreate, db: Session = Depends(get_db)):
    """Add a new domain to monitor"""
    try:
        # Check if domain already exists
        existing = db.query(models.Domain).filter(models.Domain.name == domain.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Domain '{domain.name}' already exists"
            )
        
        db_domain = models.Domain(**domain.dict())
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)
        return {"id": db_domain.id, "name": db_domain.name, "created_at": db_domain.created_at.isoformat(), "is_active": db_domain.is_active, "alert_threshold_days": db_domain.alert_threshold_days}
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error creating domain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create domain: {str(e)}"
        )

@app.get("/domains/")
def list_domains(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all monitored domains"""
    try:
        domains = db.query(models.Domain).offset(skip).limit(limit).all()
        # Convert to dict to avoid serialization issues
        return [{"id": d.id, "name": d.name, "created_at": d.created_at.isoformat(), "is_active": d.is_active, "alert_threshold_days": d.alert_threshold_days} for d in domains]
    except Exception as e:
        logger.error(f"Error listing domains: {str(e)}")
        # Return empty list instead of crashing
        return []

@app.get("/domains/{domain_id}", response_model=schemas.DomainWithChecks)
def get_domain(domain_id: int, db: Session = Depends(get_db)):
    """Get domain details with check history"""
    domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )
    
    # Get latest check
    latest_check = db.query(models.SSLCheck)\
        .filter(models.SSLCheck.domain_id == domain_id)\
        .order_by(models.SSLCheck.checked_at.desc())\
        .first()
    
    result = schemas.DomainWithChecks.from_orm(domain)
    result.latest_check = latest_check
    return result

@app.patch("/domains/{domain_id}", response_model=schemas.Domain)
def update_domain(domain_id: int, domain_update: schemas.DomainUpdate, db: Session = Depends(get_db)):
    """Update domain settings"""
    domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )
    
    update_data = domain_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(domain, field, value)
    
    db.commit()
    db.refresh(domain)
    return domain

@app.delete("/domains/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain(domain_id: int, db: Session = Depends(get_db)):
    """Delete a domain"""
    domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )
    
    db.delete(domain)
    db.commit()
    return None

# SSL Check Endpoints
@app.post("/domains/{domain_id}/check", response_model=schemas.SSLStatus)
def check_domain_ssl(domain_id: int, db: Session = Depends(get_db)):
    """Manually trigger SSL check for a domain"""
    domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )
    
    # Perform SSL check
    result = ssl_service.check_ssl_certificate(domain.name)
    
    # Save check result
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
    
    # Determine status
    status_value = "error"
    if result.get("is_valid"):
        expires_in = result.get("expires_in", 0)
        if expires_in > domain.alert_threshold_days:
            status_value = "healthy"
        elif expires_in > 0:
            status_value = "warning"
        else:
            status_value = "critical"
    
    return schemas.SSLStatus(
        domain_name=domain.name,
        is_valid=result.get("is_valid", False),
        expires_in=result.get("expires_in"),
        not_valid_after=result.get("not_valid_after"),
        last_checked=ssl_check.checked_at,
        error_message=result.get("error"),
        status=status_value
    )

@app.get("/domains/{domain_id}/ssl-status", response_model=schemas.SSLStatus)
def get_ssl_status(domain_id: int, db: Session = Depends(get_db)):
    """Get latest SSL status for a domain (from cache)"""
    domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )
    
    latest_check = db.query(models.SSLCheck)\
        .filter(models.SSLCheck.domain_id == domain_id)\
        .order_by(models.SSLCheck.checked_at.desc())\
        .first()
    
    if not latest_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No SSL checks found for domain '{domain.name}'. Try checking manually first."
        )
    
    # Determine status
    status_value = "error"
    if latest_check.is_valid:
        expires_in = latest_check.expires_in or 0
        if expires_in > domain.alert_threshold_days:
            status_value = "healthy"
        elif expires_in > 0:
            status_value = "warning"
        else:
            status_value = "critical"
    
    return schemas.SSLStatus(
        domain_name=domain.name,
        is_valid=latest_check.is_valid,
        expires_in=latest_check.expires_in,
        not_valid_after=latest_check.not_valid_after,
        last_checked=latest_check.checked_at,
        error_message=latest_check.error_message,
        status=status_value
    )

@app.get("/domains/{domain_id}/checks", response_model=List[schemas.SSLCheck])
def get_domain_checks(domain_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get SSL check history for a domain"""
    domain = db.query(models.Domain).filter(models.Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )
    
    checks = db.query(models.SSLCheck)\
        .filter(models.SSLCheck.domain_id == domain_id)\
        .order_by(models.SSLCheck.checked_at.desc())\
        .limit(limit)\
        .all()
    
    return checks

# Statistics Endpoint
@app.get("/statistics", response_model=schemas.Statistics)
def get_statistics(db: Session = Depends(get_db)):
    """Get monitoring statistics"""
    total_domains = db.query(models.Domain).count()
    active_domains = db.query(models.Domain).filter(models.Domain.is_active == True).count()
    
    # Get latest checks for each domain and calculate statistics
    from sqlalchemy import func
    subquery = db.query(
        models.SSLCheck.domain_id,
        func.max(models.SSLCheck.checked_at).label('max_checked_at')
    ).group_by(models.SSLCheck.domain_id).subquery()
    
    latest_checks = db.query(models.SSLCheck).join(
        subquery,
        (models.SSLCheck.domain_id == subquery.c.domain_id) &
        (models.SSLCheck.checked_at == subquery.c.max_checked_at)
    ).all()
    
    domains_with_errors = sum(1 for check in latest_checks if not check.is_valid)
    domains_expiring_soon = sum(
        1 for check in latest_checks 
        if check.is_valid and check.expires_in is not None and 0 < check.expires_in <= 30
    )
    domains_expired = sum(
        1 for check in latest_checks 
        if check.expires_in is not None and check.expires_in <= 0
    )
    
    return schemas.Statistics(
        total_domains=total_domains,
        active_domains=active_domains,
        domains_with_errors=domains_with_errors,
        domains_expiring_soon=domains_expiring_soon,
        domains_expired=domains_expired
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

