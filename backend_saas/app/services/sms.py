"""
SMS Notification Service
Supports multiple SMS providers: Twilio, SMS.ru, and others
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings


class SMSService:
    """SMS notification service with multiple provider support"""
    
    def __init__(self):
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        self.sms_ru_api_id = getattr(settings, 'SMS_RU_API_ID', None)
        
        # Provider priority: Twilio -> SMS.ru -> Fallback
        self.provider = self._detect_best_provider()
    
    def _detect_best_provider(self) -> str:
        """Detect the best available SMS provider"""
        if self.twilio_account_sid and self.twilio_auth_token:
            return 'twilio'
        elif self.sms_ru_api_id:
            return 'sms_ru'
        else:
            return 'none'
    
    async def send_sms(
        self, 
        phone_number: str, 
        message: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS notification
        
        Args:
            phone_number: Phone number in international format (+420123456789)
            message: SMS message text
            provider: Force specific provider (twilio, sms_ru)
        
        Returns:
            Dict with success status and details
        """
        if not phone_number or not message:
            return {
                'success': False,
                'error': 'Phone number and message are required'
            }
        
        # Clean and validate phone number
        phone_number = self._clean_phone_number(phone_number)
        if not self._validate_phone_number(phone_number):
            return {
                'success': False,
                'error': 'Invalid phone number format'
            }
        
        # Use specified provider or auto-detect
        provider = provider or self.provider
        
        if provider == 'twilio':
            return await self._send_twilio_sms(phone_number, message)
        elif provider == 'sms_ru':
            return await self._send_sms_ru_sms(phone_number, message)
        else:
            return {
                'success': False,
                'error': 'No SMS provider configured'
            }
    
    async def _send_twilio_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            auth = (self.twilio_account_sid, self.twilio_auth_token)
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            data = {
                'To': phone_number,
                'From': self.twilio_phone_number,
                'Body': message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, auth=auth)
                
                if response.status_code == 201:
                    result = response.json()
                    return {
                        'success': True,
                        'provider': 'twilio',
                        'message_id': result.get('sid'),
                        'status': result.get('status')
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Twilio error: {response.status_code} - {response.text}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Twilio SMS failed: {str(e)}'
            }
    
    async def _send_sms_ru_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via SMS.ru (popular in EU)"""
        try:
            url = "https://sms.ru/sms/send"
            
            data = {
                'api_id': self.sms_ru_api_id,
                'to': phone_number,
                'msg': message,
                'json': 1  # Get JSON response
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'OK':
                        return {
                            'success': True,
                            'provider': 'sms_ru',
                            'message_id': result.get('sms', {}).get(phone_number, {}).get('sms_id'),
                            'cost': result.get('sms', {}).get(phone_number, {}).get('cost')
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'SMS.ru error: {result.get("status_text")}'
                        }
                else:
                    return {
                        'success': False,
                        'error': f'SMS.ru HTTP error: {response.status_code}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'SMS.ru SMS failed: {str(e)}'
            }
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean and normalize phone number"""
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Add + if missing
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        return cleaned
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        # Basic validation: starts with +, 10-15 digits total
        if not phone_number.startswith('+'):
            return False
        
        digits_only = phone_number[1:]  # Remove +
        if not digits_only.isdigit():
            return False
        
        if len(digits_only) < 10 or len(digits_only) > 15:
            return False
        
        return True
    
    async def send_ssl_alert(
        self, 
        phone_number: str, 
        domain: str, 
        alert_type: str,
        days_remaining: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send SSL-specific SMS alert
        
        Args:
            phone_number: Phone number
            domain: Domain name
            alert_type: Type of alert (expires_soon, expired, renewed)
            days_remaining: Days until expiration (for expires_soon)
        """
        messages = {
            'expires_soon': f"🔒 SSL Alert: {domain} expires in {days_remaining} days. Renew now!",
            'expired': f"🚨 URGENT: SSL certificate for {domain} has EXPIRED! Immediate action required.",
            'renewed': f"✅ SSL certificate for {domain} has been renewed successfully.",
            'renewal_failed': f"❌ Failed to renew SSL certificate for {domain}. Manual intervention needed."
        }
        
        message = messages.get(alert_type, f"SSL Alert for {domain}")
        return await self.send_sms(phone_number, message)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about configured SMS providers"""
        providers = []
        
        if self.twilio_account_sid:
            providers.append({
                'name': 'Twilio',
                'configured': True,
                'phone_number': self.twilio_phone_number
            })
        
        if self.sms_ru_api_id:
            providers.append({
                'name': 'SMS.ru',
                'configured': True,
                'phone_number': 'SMS.ru service'
            })
        
        return {
            'active_provider': self.provider,
            'available_providers': providers,
            'total_providers': len(providers)
        }


# Global SMS service instance
sms_service = SMSService()
