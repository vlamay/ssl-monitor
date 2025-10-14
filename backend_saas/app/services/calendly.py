"""
Calendly integration service for SSL Monitor Pro
"""
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CalendlyService:
    """Calendly service for SSL Monitor Pro"""
    
    def __init__(self):
        self.api_token = "eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzYwNDc5MzMyLCJqdGkiOiIyYzk5ODY3Yi01NmJlLTQ4ZjEtODdhNS0xMDQ1ZGQ4NzlkYjYiLCJ1c2VyX3V1aWQiOiI0OTliYTY4OC0yMzBlLTQxNzUtYWZkMS00MDk5NTIwNTYwODAifQ.BoGSD4VXK1oZEPy3ayVLZ3pGp5diiIJgiPETedEOyWLENPu1rX8Q3T3oy9mxoxLZFwVm9BX6s5jJ4eOjZ4idbA"
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "SSL-Monitor-Pro/1.0"
        }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get Calendly user info: {e}")
            return {"error": str(e)}
    
    async def get_event_types(self, user_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available event types for booking"""
        try:
            params = {}
            if user_uri:
                params["user"] = user_uri
            else:
                # Get user URI first
                user_info = await self.get_user_info()
                if "resource" in user_info:
                    params["user"] = user_info["resource"]["uri"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/event_types",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("collection", [])
        except Exception as e:
            logger.error(f"Failed to get Calendly event types: {e}")
            return []
    
    async def create_demo_booking_link(self, 
                                     user_email: str,
                                     user_name: str,
                                     company: str = "",
                                     message: str = "") -> Dict[str, Any]:
        """Create a demo booking link with pre-filled information"""
        try:
            # Get user info and event types
            user_info = await self.get_user_info()
            event_types = await self.get_event_types()
            
            if not event_types:
                # Fallback to WhatsApp if no event types available
                return {
                    "status": "fallback",
                    "whatsapp_url": f"https://wa.me/420721579603?text={self._get_whatsapp_demo_message(user_name, company, message)}",
                    "message": "Calendly not available, redirecting to WhatsApp"
                }
            
            # Use first available event type for demo
            demo_event = event_types[0]
            event_uri = demo_event["uri"]
            
            # Create booking link with pre-filled information
            booking_url = f"{event_uri}?name={user_name}&email={user_email}"
            if company:
                booking_url += f"&a1={company}"
            if message:
                booking_url += f"&a2={message}"
            
            return {
                "status": "success",
                "booking_url": booking_url,
                "event_type": demo_event["name"],
                "duration": demo_event.get("duration", 30),
                "calendly_user": user_info.get("resource", {}).get("name", "SSL Monitor Pro")
            }
            
        except Exception as e:
            logger.error(f"Failed to create Calendly booking: {e}")
            # Fallback to WhatsApp
            return {
                "status": "fallback",
                "whatsapp_url": f"https://wa.me/420721579603?text={self._get_whatsapp_demo_message(user_name, company, message)}",
                "error": str(e)
            }
    
    async def get_scheduled_events(self, user_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get scheduled events"""
        try:
            params = {}
            if user_uri:
                params["user"] = user_uri
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/scheduled_events",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("collection", [])
        except Exception as e:
            logger.error(f"Failed to get scheduled events: {e}")
            return []
    
    def _get_whatsapp_demo_message(self, user_name: str, company: str, message: str) -> str:
        """Generate WhatsApp demo message"""
        whatsapp_message = f"🎯 Request SSL Monitor Pro Demo\n\n"
        whatsapp_message += f"Name: {user_name}\n"
        if company:
            whatsapp_message += f"Company: {company}\n"
        if message:
            whatsapp_message += f"Message: {message}\n"
        whatsapp_message += "\nInterested in enterprise SSL monitoring solution!"
        return whatsapp_message
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Calendly API is accessible"""
        try:
            user_info = await self.get_user_info()
            if "error" in user_info:
                return {"status": "error", "message": user_info["error"]}
            else:
                return {
                    "status": "healthy",
                    "user": user_info.get("resource", {}).get("name", "Unknown"),
                    "email": user_info.get("resource", {}).get("email", "Unknown")
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Global instance
calendly_service = CalendlyService()
