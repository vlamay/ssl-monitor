"""
Calendly booking API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.services.calendly import calendly_service
from app.core.config import settings

router = APIRouter()

class BookingRequest(BaseModel):
    user_name: str
    user_email: EmailStr
    company: Optional[str] = ""
    message: Optional[str] = ""

class BookingResponse(BaseModel):
    status: str
    booking_url: Optional[str] = None
    whatsapp_url: Optional[str] = None
    event_type: Optional[str] = None
    duration: Optional[int] = None
    calendly_user: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

@router.get("/health", summary="Check Calendly API health", response_model=dict)
async def check_calendly_health():
    """
    Check if Calendly API is accessible and working
    """
    try:
        health_status = await calendly_service.health_check()
        return health_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Calendly service unavailable: {str(e)}"
        )

@router.get("/user-info", summary="Get Calendly user information", response_model=dict)
async def get_calendly_user_info():
    """
    Get current Calendly user information
    """
    try:
        user_info = await calendly_service.get_user_info()
        if "error" in user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=user_info["error"]
            )
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.get("/event-types", summary="Get available event types", response_model=dict)
async def get_event_types():
    """
    Get available event types for booking
    """
    try:
        event_types = await calendly_service.get_event_types()
        return {
            "status": "success",
            "event_types": event_types,
            "count": len(event_types)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event types: {str(e)}"
        )

@router.post("/create-booking", summary="Create demo booking link", response_model=BookingResponse)
async def create_demo_booking(request: BookingRequest):
    """
    Create a demo booking link with pre-filled information.
    Falls back to WhatsApp if Calendly is unavailable.
    """
    try:
        result = await calendly_service.create_demo_booking_link(
            user_email=request.user_email,
            user_name=request.user_name,
            company=request.company,
            message=request.message
        )
        
        return BookingResponse(**result)
        
    except Exception as e:
        # Fallback to WhatsApp on any error
        whatsapp_message = f"🎯 Request SSL Monitor Pro Demo\n\nName: {request.user_name}\nEmail: {request.user_email}\n"
        if request.company:
            whatsapp_message += f"Company: {request.company}\n"
        if request.message:
            whatsapp_message += f"Message: {request.message}\n"
        whatsapp_message += "\nInterested in enterprise SSL monitoring solution!"
        
        return BookingResponse(
            status="fallback",
            whatsapp_url=f"https://wa.me/420721579603?text={whatsapp_message}",
            message="Calendly unavailable, redirecting to WhatsApp",
            error=str(e)
        )

@router.get("/quick-demo", summary="Quick demo booking", response_model=BookingResponse)
async def quick_demo_booking(
    name: str,
    email: EmailStr,
    company: Optional[str] = None,
    message: Optional[str] = None
):
    """
    Quick demo booking endpoint for frontend integration
    """
    request = BookingRequest(
        user_name=name,
        user_email=email,
        company=company or "",
        message=message or ""
    )
    return await create_demo_booking(request)

@router.get("/scheduled-events", summary="Get scheduled events", response_model=dict)
async def get_scheduled_events():
    """
    Get upcoming scheduled events
    """
    try:
        events = await calendly_service.get_scheduled_events()
        return {
            "status": "success",
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduled events: {str(e)}"
        )

# Frontend integration helpers
@router.get("/widget-config", summary="Get widget configuration", response_model=dict)
async def get_widget_config():
    """
    Get configuration for Calendly widget integration
    """
    try:
        user_info = await calendly_service.get_user_info()
        event_types = await calendly_service.get_event_types()
        
        if "error" in user_info or not event_types:
            return {
                "available": False,
                "fallback_url": "https://wa.me/420721579603?text=Hello!%20I'm%20interested%20in%20SSL%20Monitor%20Pro%20demo.",
                "message": "Calendly not available, using WhatsApp fallback"
            }
        
        # Use first event type for demo
        demo_event = event_types[0]
        
        return {
            "available": True,
            "user_uri": user_info.get("resource", {}).get("uri"),
            "event_type_uri": demo_event["uri"],
            "event_name": demo_event["name"],
            "duration": demo_event.get("duration", 30),
            "widget_url": f"https://calendly.com/{demo_event['slug']}",
            "embed_url": f"https://calendly.com/{demo_event['slug']}/embed"
        }
        
    except Exception as e:
        return {
            "available": False,
            "fallback_url": "https://wa.me/420721579603?text=Hello!%20I'm%20interested%20in%20SSL%20Monitor%20Pro%20demo.",
            "error": str(e)
        }
