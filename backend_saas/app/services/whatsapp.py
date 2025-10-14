"""
WhatsApp Business integration service
"""
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """WhatsApp Business service for SSL Monitor Pro"""
    
    def __init__(self):
        self.phone_number = "+420 721 579 603"
        self.whatsapp_url = "https://wa.me/420721579603"
        self.business_name = "SSL Monitor Pro"
    
    def get_contact_url(self, message: str = None) -> str:
        """
        Generate WhatsApp contact URL
        
        Args:
            message: Pre-filled message
            
        Returns:
            WhatsApp URL
        """
        if message:
            # URL encode the message
            import urllib.parse
            encoded_message = urllib.parse.quote(message)
            return f"{self.whatsapp_url}?text={encoded_message}"
        return self.whatsapp_url
    
    def get_ssl_alert_message(self, domain: str, days_until_expiry: int) -> str:
        """
        Generate SSL alert message for WhatsApp
        
        Args:
            domain: Domain name
            days_until_expiry: Days until certificate expires
            
        Returns:
            Formatted message
        """
        if days_until_expiry <= 0:
            status_emoji = "🚨"
            status_text = "EXPIRED"
        elif days_until_expiry <= 1:
            status_emoji = "🔴"
            status_text = "EXPIRING TODAY"
        elif days_until_expiry <= 3:
            status_emoji = "🟠"
            status_text = "EXPIRING SOON"
        elif days_until_expiry <= 7:
            status_emoji = "🟡"
            status_text = "EXPIRING THIS WEEK"
        else:
            status_emoji = "⚠️"
            status_text = "EXPIRING SOON"
        
        message = f"""🔐 *SSL Certificate Alert* {status_emoji}

*Domain:* {domain}
*Status:* {status_text}
*Days until expiry:* {days_until_expiry}

🚀 *SSL Monitor Pro* is monitoring your certificates 24/7

Need help? Contact us for immediate assistance!"""
        
        return message
    
    def get_welcome_message(self, user_name: str = None) -> str:
        """
        Generate welcome message for new users
        
        Args:
            user_name: User's name
            
        Returns:
            Welcome message
        """
        greeting = f"Hi {user_name}!" if user_name else "Hello!"
        
        message = f"""🎉 {greeting} Welcome to *SSL Monitor Pro*!

🔐 *Your SSL certificates are now protected*

✅ *What you get:*
• 24/7 certificate monitoring
• Instant expiry alerts
• Multi-channel notifications
• Enterprise-grade security

🚀 *Need help getting started?*
We're here to help you secure your domains!

*Contact:* +420 721 579 603"""
        
        return message
    
    def get_support_message(self, issue_type: str = None) -> str:
        """
        Generate support message
        
        Args:
            issue_type: Type of issue (billing, technical, etc.)
            
        Returns:
            Support message
        """
        message = f"""🆘 *SSL Monitor Pro Support*

We're here to help with your SSL monitoring needs!

📞 *Contact:* +420 721 579 603
⏰ *Available:* Mon-Fri 9:00-17:00 CET

🔧 *We can help with:*
• SSL certificate setup
• Monitoring configuration
• Billing questions
• Technical support
• Custom integrations

*Issue type:* {issue_type if issue_type else 'General inquiry'}

We'll get back to you within 1 hour during business hours!"""
        
        return message
    
    def get_demo_request_message(self, company: str = None) -> str:
        """
        Generate demo request message
        
        Args:
            company: Company name
            
        Returns:
            Demo request message
        """
        company_text = f" from {company}" if company else ""
        
        message = f"""🎯 *Request SSL Monitor Pro Demo*

Hi! I'd like to schedule a demo{company_text}.

🏢 *Company:* {company if company else 'Not specified'}
📅 *Preferred time:* [Please specify]
👥 *Attendees:* [Number of people]
🎯 *Use case:* [SSL monitoring needs]

🔐 *Interested in:*
• Enterprise features
• Custom monitoring
• API integration
• Team collaboration

📞 *Contact:* +420 721 579 603
⏰ *Available:* Mon-Fri 9:00-17:00 CET

Looking forward to showing you how SSL Monitor Pro can secure your infrastructure!"""
        
        return message
    
    async def send_notification(
        self, 
        phone_number: str, 
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Send WhatsApp notification (placeholder for future WhatsApp Business API)
        
        Args:
            phone_number: Recipient phone number
            message: Message content
            message_type: Type of message (text, alert, etc.)
            
        Returns:
            Send result
        """
        # TODO: Implement WhatsApp Business API integration
        # For now, return the URL for manual sending
        
        logger.info(f"WhatsApp notification prepared for {phone_number}: {message[:50]}...")
        
        whatsapp_url = self.get_contact_url(message)
        
        return {
            "status": "prepared",
            "whatsapp_url": whatsapp_url,
            "phone_number": phone_number,
            "message": message,
            "message_type": message_type,
            "note": "Use WhatsApp Business API for automated sending"
        }
    
    def get_qr_code_data(self) -> Dict[str, Any]:
        """
        Get QR code data for WhatsApp contact
        
        Returns:
            QR code data
        """
        return {
            "phone_number": self.phone_number,
            "whatsapp_url": self.whatsapp_url,
            "qr_code_text": f"Contact {self.business_name} on WhatsApp: {self.phone_number}",
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={self.whatsapp_url}"
        }
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for WhatsApp
        
        Args:
            phone_number: Phone number to format
            
        Returns:
            Formatted phone number
        """
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if missing
        if not digits_only.startswith('420'):
            digits_only = '420' + digits_only.lstrip('0')
        
        return f"+{digits_only}"


# Global WhatsApp service instance
whatsapp_service = WhatsAppService()
