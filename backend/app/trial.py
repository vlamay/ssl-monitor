"""
Trial signup API for SSL Monitor Pro
Handles trial account creation and onboarding
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from database import get_db
from utils.telegram import send_telegram_alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trial", tags=["trial"])

# Pydantic models
class TrialSignupRequest(BaseModel):
    """Trial signup request model"""
    email: str
    company: str
    phone: Optional[str] = None
    website: Optional[str] = None
    domains_count: Optional[int] = None

class TrialSignupResponse(BaseModel):
    """Trial signup response model"""
    success: bool
    trial_id: str
    trial_ends_at: str
    onboarding_url: str
    telegram_setup_url: str
    message: str

@router.post("/signup")
async def trial_signup(
    request: TrialSignupRequest,
    db: Session = Depends(get_db)
):
    """Create a new trial account"""
    try:
        # Generate trial ID
        trial_id = f"trial_{int(datetime.now().timestamp())}"
        trial_ends_at = datetime.now() + timedelta(days=14)
        
        # Create trial account record (you can store this in database)
        trial_data = {
            "trial_id": trial_id,
            "email": request.email,
            "company": request.company,
            "phone": request.phone,
            "website": request.website,
            "domains_count": request.domains_count,
            "created_at": datetime.now().isoformat(),
            "trial_ends_at": trial_ends_at.isoformat(),
            "status": "active"
        }
        
        # Send Telegram notification about new trial
        telegram_message = f"""
🎉 <b>Nový Trial Účet</b>

📧 Email: {request.email}
🏢 Firma: {request.company}
📱 Telefon: {request.phone or 'Neuvedeno'}
🌐 Web: {request.website or 'Neuvedeno'}
📊 Počet domén: {request.domains_count or 'Neuvedeno'}

🆔 Trial ID: {trial_id}
📅 Trial končí: {trial_ends_at.strftime('%d.%m.%Y')}

⚡ <i>Okamžitě kontaktovat pro onboarding!</i>
        """
        
        send_telegram_alert(telegram_message)
        
        # Log trial creation
        logger.info(f"New trial created: {request.email} - {request.company}")
        
        return TrialSignupResponse(
            success=True,
            trial_id=trial_id,
            trial_ends_at=trial_ends_at.isoformat(),
            onboarding_url=f"https://ssl-monitor-pro.onrender.com/onboarding.html?trial_id={trial_id}",
            telegram_setup_url=f"https://ssl-monitor-api.onrender.com/telegram/setup?trial_id={trial_id}",
            message="Trial účet byl úspěšně vytvořen. Zkontrolujte váš email pro další instrukce."
        )
        
    except Exception as e:
        logger.error(f"Trial signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nepodařilo se vytvořit trial účet: {str(e)}"
        )

@router.get("/status/{trial_id}")
async def get_trial_status(trial_id: str, db: Session = Depends(get_db)):
    """Get trial account status"""
    try:
        # In a real implementation, you would query the database
        # For now, return mock data
        return {
            "trial_id": trial_id,
            "status": "active",
            "days_remaining": 14,
            "domains_added": 0,
            "alerts_sent": 0,
            "last_check": None
        }
    except Exception as e:
        logger.error(f"Trial status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nepodařilo se získat stav trial účtu: {str(e)}"
        )

@router.post("/convert/{trial_id}")
async def convert_trial_to_paid(
    trial_id: str,
    plan: str,
    db: Session = Depends(get_db)
):
    """Convert trial account to paid subscription"""
    try:
        # In a real implementation, you would:
        # 1. Validate trial_id exists and is active
        # 2. Create Stripe subscription
        # 3. Update trial status to "converted"
        # 4. Send confirmation email
        
        return {
            "success": True,
            "message": "Trial účet byl úspěšně převeden na placené předplatné",
            "plan": plan,
            "subscription_id": f"sub_{trial_id}",
            "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trial conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nepodařilo se převést trial účet: {str(e)}"
        )

@router.get("/test")
async def test_trial_endpoint():
    """Test trial endpoint"""
    return {
        "status": "ok",
        "message": "Trial API endpoint is working",
        "timestamp": datetime.now().isoformat()
    }
