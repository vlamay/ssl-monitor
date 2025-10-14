"""
WhatsApp contact endpoints
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from app.services.whatsapp import whatsapp_service
from app.api.v1.users.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


class WhatsAppContactRequest(BaseModel):
    """WhatsApp contact request"""
    message: Optional[str] = None
    message_type: Optional[str] = "general"


class WhatsAppContactResponse(BaseModel):
    """WhatsApp contact response"""
    whatsapp_url: str
    phone_number: str
    message: str
    qr_code_url: str


@router.get("/contact", response_model=WhatsAppContactResponse)
async def get_whatsapp_contact(
    message: Optional[str] = Query(None, description="Pre-filled message"),
    message_type: str = Query("general", description="Type of message")
) -> WhatsAppContactResponse:
    """Get WhatsApp contact information"""
    
    # Format message based on type
    if message_type == "ssl_alert" and not message:
        message = whatsapp_service.get_ssl_alert_message("example.com", 7)
    elif message_type == "support" and not message:
        message = whatsapp_service.get_support_message()
    elif message_type == "demo" and not message:
        message = whatsapp_service.get_demo_request_message()
    elif message_type == "welcome" and not message:
        message = whatsapp_service.get_welcome_message()
    elif not message:
        message = f"Hello! I'm interested in SSL Monitor Pro services."
    
    # Get WhatsApp URL
    whatsapp_url = whatsapp_service.get_contact_url(message)
    
    # Get QR code data
    qr_data = whatsapp_service.get_qr_code_data()
    
    return WhatsAppContactResponse(
        whatsapp_url=whatsapp_url,
        phone_number=whatsapp_service.phone_number,
        message=message,
        qr_code_url=qr_data["qr_code_url"]
    )


@router.get("/contact/qr")
async def get_whatsapp_qr_code() -> Dict[str, Any]:
    """Get WhatsApp QR code for easy contact"""
    
    qr_data = whatsapp_service.get_qr_code_data()
    
    return {
        "qr_code_url": qr_data["qr_code_url"],
        "whatsapp_url": qr_data["whatsapp_url"],
        "phone_number": qr_data["phone_number"],
        "business_name": whatsapp_service.business_name,
        "instructions": "Scan this QR code with your phone to contact SSL Monitor Pro on WhatsApp"
    }


@router.post("/contact/send")
async def send_whatsapp_message(
    request: WhatsAppContactRequest,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Send WhatsApp message (returns URL for manual sending)"""
    
    # Get WhatsApp URL with message
    whatsapp_url = whatsapp_service.get_contact_url(request.message)
    
    # For now, return the URL for manual sending
    # TODO: Implement WhatsApp Business API for automated sending
    
    return {
        "status": "success",
        "whatsapp_url": whatsapp_url,
        "phone_number": whatsapp_service.phone_number,
        "message": request.message,
        "note": "Click the URL to open WhatsApp with the pre-filled message"
    }


@router.get("/contact/alert/{domain}")
async def get_ssl_alert_whatsapp(
    domain: str,
    days_until_expiry: int = Query(7, description="Days until certificate expires")
) -> Dict[str, Any]:
    """Get WhatsApp URL for SSL certificate alert"""
    
    message = whatsapp_service.get_ssl_alert_message(domain, days_until_expiry)
    whatsapp_url = whatsapp_service.get_contact_url(message)
    
    return {
        "domain": domain,
        "days_until_expiry": days_until_expiry,
        "whatsapp_url": whatsapp_url,
        "phone_number": whatsapp_service.phone_number,
        "message": message,
        "alert_level": "critical" if days_until_expiry <= 1 else "warning" if days_until_expiry <= 7 else "info"
    }


@router.get("/contact/support")
async def get_support_whatsapp(
    issue_type: Optional[str] = Query(None, description="Type of support issue")
) -> Dict[str, Any]:
    """Get WhatsApp URL for support contact"""
    
    message = whatsapp_service.get_support_message(issue_type)
    whatsapp_url = whatsapp_service.get_contact_url(message)
    
    return {
        "issue_type": issue_type or "general",
        "whatsapp_url": whatsapp_url,
        "phone_number": whatsapp_service.phone_number,
        "message": message,
        "response_time": "1 hour during business hours (Mon-Fri 9:00-17:00 CET)"
    }


@router.get("/contact/demo")
async def get_demo_whatsapp(
    company: Optional[str] = Query(None, description="Company name")
) -> Dict[str, Any]:
    """Get WhatsApp URL for demo request"""
    
    message = whatsapp_service.get_demo_request_message(company)
    whatsapp_url = whatsapp_service.get_contact_url(message)
    
    return {
        "company": company,
        "whatsapp_url": whatsapp_url,
        "phone_number": whatsapp_service.phone_number,
        "message": message,
        "demo_duration": "30 minutes",
        "availability": "Mon-Fri 9:00-17:00 CET"
    }


@router.get("/contact/welcome")
async def get_welcome_whatsapp(
    user_name: Optional[str] = Query(None, description="User name")
) -> Dict[str, Any]:
    """Get WhatsApp URL for welcome message"""
    
    message = whatsapp_service.get_welcome_message(user_name)
    whatsapp_url = whatsapp_service.get_contact_url(message)
    
    return {
        "user_name": user_name,
        "whatsapp_url": whatsapp_url,
        "phone_number": whatsapp_service.phone_number,
        "message": message,
        "welcome_features": [
            "24/7 certificate monitoring",
            "Instant expiry alerts",
            "Multi-channel notifications",
            "Enterprise-grade security"
        ]
    }


@router.get("/info")
async def get_whatsapp_info() -> Dict[str, Any]:
    """Get WhatsApp Business information"""
    
    return {
        "business_name": whatsapp_service.business_name,
        "phone_number": whatsapp_service.phone_number,
        "whatsapp_url": whatsapp_service.whatsapp_url,
        "services": [
            "SSL Certificate Monitoring",
            "Technical Support",
            "Demo Requests",
            "Billing Support",
            "Custom Integrations"
        ],
        "availability": "Mon-Fri 9:00-17:00 CET",
        "response_time": "1 hour during business hours",
        "languages": ["English", "Czech"],
        "features": [
            "Instant SSL alerts",
            "24/7 monitoring support",
            "Enterprise solutions",
            "API integrations",
            "Custom notifications"
        ]
    }
