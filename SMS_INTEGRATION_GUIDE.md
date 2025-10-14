# 📱 SMS Integration Guide - SSL Monitor Pro

## 🎯 Overview

SSL Monitor Pro now supports SMS notifications through multiple providers, giving you instant alerts about SSL certificate issues directly to your mobile phone.

## 🚀 Features

- **Multi-provider support**: Twilio (global) and SMS.ru (EU-focused)
- **Automatic provider selection**: Uses the best available provider
- **Phone number validation**: International format validation
- **Custom message templates**: SSL-specific alert messages
- **Test functionality**: Send test SMS to verify setup

## 🔧 Setup Instructions

### Option 1: Twilio (Recommended for Global)

1. **Sign up for Twilio**:
   - Go to [twilio.com](https://www.twilio.com)
   - Create account and verify phone number
   - Get Account SID and Auth Token from dashboard

2. **Purchase a phone number**:
   - Buy a Twilio phone number for sending SMS
   - Note the phone number (format: +1234567890)

3. **Configure environment variables**:
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Option 2: SMS.ru (Recommended for EU)

1. **Sign up for SMS.ru**:
   - Go to [sms.ru](https://sms.ru)
   - Register and get API ID
   - Add funds to your account

2. **Configure environment variable**:
   ```bash
   SMS_RU_API_ID=your_api_id_here
   ```

## 📱 API Endpoints

### Get SMS Notifications
```http
GET /api/v1/sms/
Authorization: Bearer <token>
```

### Create SMS Notification
```http
POST /api/v1/sms/
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "+420123456789",
  "enabled": true,
  "triggers": ["expires_in_30d", "expires_in_7d", "expires_in_1d", "expired"]
}
```

### Update SMS Notification
```http
PUT /api/v1/sms/{notification_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "+420987654321",
  "enabled": false
}
```

### Delete SMS Notification
```http
DELETE /api/v1/sms/{notification_id}
Authorization: Bearer <token>
```

### Test SMS
```http
POST /api/v1/sms/test
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "+420123456789",
  "message": "Custom test message"
}
```

### Get SMS Providers
```http
GET /api/v1/sms/providers
Authorization: Bearer <token>
```

## 📋 Phone Number Formats

### Supported Formats:
- `+420123456789` (Czech Republic)
- `+1234567890` (United States)
- `+49123456789` (Germany)
- `+33123456789` (France)

### Validation Rules:
- Must start with `+`
- 10-15 digits total (excluding `+`)
- Country code must be 1-3 digits
- Local number must be 7-12 digits

## 🔔 Message Templates

### SSL Certificate Expiration
```
SSL Alert: example.com expires in 7 days. Renew now!
```

### SSL Certificate Expired
```
URGENT: SSL certificate for example.com has EXPIRED! Immediate action required.
```

### Welcome Message
```
Welcome to SSL Monitor Pro, John Doe! Your SSL monitoring is now active.
```

### Support Request
```
SSL Monitor Pro Support: We received your support request. We'll contact you soon.
```

### Demo Request
```
Demo request for Your Company confirmed. We'll schedule a call soon.
```

## 💰 Cost Considerations

### Twilio Pricing:
- **SMS to US/Canada**: $0.0075 per message
- **SMS to Europe**: $0.05-0.15 per message
- **Phone number**: $1/month

### SMS.ru Pricing:
- **SMS to Russia**: ~$0.02 per message
- **SMS to Europe**: ~$0.05-0.10 per message
- **No monthly fees**

### Cost Optimization Tips:
1. **Use email as primary**: SMS for critical alerts only
2. **Group notifications**: Avoid sending multiple SMS for same domain
3. **Set reasonable triggers**: Don't notify for every minor change
4. **Monitor usage**: Track SMS costs in dashboard

## 🛠️ Troubleshooting

### Common Issues:

#### "SMS service not configured"
- **Solution**: Configure at least one SMS provider
- **Check**: Environment variables are set correctly

#### "Invalid phone number format"
- **Solution**: Use international format with country code
- **Example**: `+420123456789` instead of `420123456789`

#### "SMS sending failed"
- **Solution**: Check provider credentials and account balance
- **Check**: Phone number is valid and reachable

#### "Provider not responding"
- **Solution**: Check internet connection and provider status
- **Fallback**: Switch to alternative provider if configured

### Debug Steps:
1. **Test SMS endpoint**: Use `/api/v1/sms/test`
2. **Check provider status**: Use `/api/v1/sms/providers`
3. **Verify credentials**: Check environment variables
4. **Check account balance**: Ensure sufficient funds

## 🔒 Security & Privacy

### Data Protection:
- Phone numbers are encrypted in database
- SMS content is not logged permanently
- Provider credentials are environment-only
- GDPR compliant data handling

### Best Practices:
- Use HTTPS for all API calls
- Store credentials in environment variables
- Regularly rotate API keys
- Monitor for unusual SMS activity

## 📊 Monitoring & Analytics

### Metrics to Track:
- SMS delivery success rate
- Cost per notification
- User engagement with SMS alerts
- Provider performance comparison

### Dashboard Integration:
- SMS notification status in user dashboard
- Cost tracking and alerts
- Delivery confirmation logs
- Provider health monitoring

## 🚀 Future Enhancements

### Planned Features:
- **Two-way SMS**: Reply to SMS for quick actions
- **SMS scheduling**: Send SMS at specific times
- **Rich messaging**: Include links in SMS
- **Group SMS**: Send to multiple numbers
- **SMS templates**: Custom message templates
- **Delivery tracking**: Real-time delivery status

### Integration Opportunities:
- **WhatsApp Business**: Combine with existing WhatsApp
- **Push notifications**: Mobile app notifications
- **Voice calls**: Critical alert escalation
- **Slack integration**: Team notification channels

---

## 📞 Support

For SMS integration support:
- **Email**: support@sslmonitor.pro
- **Documentation**: [docs.sslmonitor.pro](https://docs.sslmonitor.pro)
- **API Status**: [status.sslmonitor.pro](https://status.sslmonitor.pro)

**Ready to get instant SSL alerts via SMS? Start with the free plan and add SMS notifications to never miss a certificate expiration again!** 🚀
