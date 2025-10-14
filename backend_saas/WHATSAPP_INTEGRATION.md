# 📱 WhatsApp Business Integration - SSL Monitor Pro

## 🚀 Overview

SSL Monitor Pro now includes comprehensive WhatsApp Business integration with phone number **+420 721 579 603** for enhanced customer communication and support.

## ✨ Features

### 📞 Contact Methods
- **Direct WhatsApp Contact**: Click-to-chat functionality
- **QR Code Integration**: Easy mobile contact scanning
- **Pre-filled Messages**: Contextual message templates
- **Multi-language Support**: English and Czech

### 🔔 Notification Types
- **SSL Certificate Alerts**: Expiry warnings and notifications
- **Support Messages**: Technical assistance requests
- **Demo Requests**: Product demonstration scheduling
- **Welcome Messages**: New user onboarding

### 🎯 Use Cases
- **SSL Alert Notifications**: Instant alerts for certificate expiry
- **Customer Support**: 24/7 technical assistance
- **Sales Inquiries**: Demo requests and pricing information
- **Account Management**: Billing and subscription support

## 🛠️ API Endpoints

### Contact Information
```bash
# Get WhatsApp contact info
GET /api/v1/whatsapp/contact

# Get QR code for easy contact
GET /api/v1/whatsapp/contact/qr

# Get business information
GET /api/v1/whatsapp/info
```

### Specialized Messages
```bash
# SSL Alert WhatsApp URL
GET /api/v1/whatsapp/contact/alert/{domain}?days_until_expiry=7

# Support Contact WhatsApp URL
GET /api/v1/whatsapp/contact/support?issue_type=technical

# Demo Request WhatsApp URL
GET /api/v1/whatsapp/contact/demo?company=ExampleCorp

# Welcome Message WhatsApp URL
GET /api/v1/whatsapp/contact/welcome?user_name=John
```

## 💻 Frontend Integration

### WhatsApp Widget
Include the WhatsApp widget in your frontend:

```html
<!-- WhatsApp Widget -->
<div class="whatsapp-widget">
    <a href="https://wa.me/420721579603?text=Hello!%20I'm%20interested%20in%20SSL%20Monitor%20Pro%20services." 
       class="whatsapp-button" 
       target="_blank" 
       rel="noopener noreferrer">
        <svg class="whatsapp-icon" viewBox="0 0 24 24">
            <!-- WhatsApp SVG icon -->
        </svg>
    </a>
</div>
```

### JavaScript Functions
```javascript
// Update WhatsApp message dynamically
function updateWhatsAppMessage(message) {
    const encodedMessage = encodeURIComponent(message);
    const whatsappButton = document.querySelector('.whatsapp-button');
    whatsappButton.href = `https://wa.me/420721579603?text=${encodedMessage}`;
}

// Show SSL alert message
function showSSLAlert(domain, daysUntilExpiry) {
    let message = `🔐 SSL Certificate Alert 🚨\n\nDomain: ${domain}\nDays until expiry: ${daysUntilExpiry}\n\nNeed immediate assistance!`;
    updateWhatsAppMessage(message);
}

// Show support message
function showSupportMessage(issueType = 'general') {
    let message = `🆘 SSL Monitor Pro Support\n\nIssue type: ${issueType}\n\nNeed help with SSL monitoring!`;
    updateWhatsAppMessage(message);
}
```

## 📱 Message Templates

### SSL Certificate Alert
```
🔐 *SSL Certificate Alert* 🚨

*Domain:* example.com
*Status:* EXPIRING SOON
*Days until expiry:* 7

🚀 *SSL Monitor Pro* is monitoring your certificates 24/7

Need help? Contact us for immediate assistance!
```

### Support Request
```
🆘 *SSL Monitor Pro Support*

We're here to help with your SSL monitoring needs!

📞 *Contact:* +420 721 579 603
⏰ *Available:* Mon-Fri 9:00-17:00 CET

🔧 *We can help with:*
• SSL certificate setup
• Monitoring configuration
• Billing questions
• Technical support
• Custom integrations

We'll get back to you within 1 hour during business hours!
```

### Demo Request
```
🎯 *Request SSL Monitor Pro Demo*

Hi! I'd like to schedule a demo from ExampleCorp.

🏢 *Company:* ExampleCorp
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

Looking forward to showing you how SSL Monitor Pro can secure your infrastructure!
```

## 🔧 Configuration

### Environment Variables
```bash
# WhatsApp Business Configuration
WHATSAPP_PHONE=+420721579603
WHATSAPP_BUSINESS_NAME="SSL Monitor Pro"
```

### Database Schema
```sql
-- WhatsApp phone field in notifications table
ALTER TABLE notifications ADD COLUMN whatsapp_phone VARCHAR(20);

-- Example notification with WhatsApp
INSERT INTO notifications (
    user_id, 
    type, 
    enabled, 
    whatsapp_phone, 
    triggers
) VALUES (
    1, 
    'whatsapp', 
    true, 
    '+420721579603', 
    '["expires_in_7d", "expires_in_1d", "expired"]'
);
```

## 📊 Analytics & Tracking

### Google Analytics Integration
```javascript
// Track WhatsApp contact clicks
gtag('event', 'whatsapp_contact', {
    'event_category': 'engagement',
    'event_label': 'whatsapp_widget'
});
```

### Custom Analytics
```javascript
// Track different message types
analytics.track('WhatsApp Contact Clicked', {
    source: 'widget',
    phone: '+420721579603',
    message_type: 'ssl_alert',
    domain: 'example.com'
});
```

## 🚀 Deployment

### Render.com Configuration
```yaml
# Add to render.yaml
envVars:
  - key: WHATSAPP_PHONE
    value: "+420721579603"
  - key: WHATSAPP_BUSINESS_NAME
    value: "SSL Monitor Pro"
```

### Docker Configuration
```dockerfile
# Add WhatsApp widget to static files
COPY static/ /app/static/
```

## 📈 Usage Examples

### 1. SSL Certificate Alert
```python
# Backend: Trigger WhatsApp alert
from app.services.whatsapp import whatsapp_service

message = whatsapp_service.get_ssl_alert_message("example.com", 7)
whatsapp_url = whatsapp_service.get_contact_url(message)
```

### 2. Customer Support
```python
# Backend: Generate support message
message = whatsapp_service.get_support_message("billing")
whatsapp_url = whatsapp_service.get_contact_url(message)
```

### 3. Demo Request
```python
# Backend: Create demo request message
message = whatsapp_service.get_demo_request_message("TechCorp")
whatsapp_url = whatsapp_service.get_contact_url(message)
```

## 🔒 Security & Privacy

### Data Protection
- Phone numbers are stored securely
- Messages are not logged for privacy
- GDPR compliant data handling
- Secure API endpoints

### Rate Limiting
- WhatsApp contact endpoints are rate limited
- Prevents spam and abuse
- IP-based throttling

## 📞 Business Hours

- **Monday - Friday**: 9:00 - 17:00 CET
- **Response Time**: Within 1 hour during business hours
- **Languages**: English, Czech
- **Phone**: +420 721 579 603

## 🆘 Support

### WhatsApp Business Features
- ✅ Business profile verification
- ✅ Automated message templates
- ✅ Quick replies
- ✅ Business hours display
- ✅ Website integration

### Contact Information
- **Phone**: +420 721 579 603
- **Business Name**: SSL Monitor Pro
- **Services**: SSL Monitoring, Technical Support, Sales
- **Website**: https://ssl-monitor.pages.dev

## 🎯 Next Steps

1. **Deploy WhatsApp Integration**: Add to production environment
2. **Configure Notifications**: Set up SSL alert notifications
3. **Add Frontend Widget**: Include WhatsApp button on website
4. **Test Integration**: Verify all message types work correctly
5. **Monitor Usage**: Track WhatsApp engagement metrics

---

**WhatsApp Business Integration** - Enhanced customer communication for SSL Monitor Pro 📱✨
