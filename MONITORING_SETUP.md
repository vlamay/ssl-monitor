# 📊 Monitoring Setup Guide

## 🎯 Health Check Endpoints

### Backend API Health
```bash
# Basic health check
curl https://ssl-monitor-backend.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-10-11T20:30:00Z"
}
```

### Database Health
```bash
# Test database connection
curl https://ssl-monitor-backend.onrender.com/health/database

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "tables": ["domains", "ssl_checks"],
  "count": 42
}
```

### Redis Health
```bash
# Test Redis connection
curl https://ssl-monitor-backend.onrender.com/health/redis

# Expected response:
{
  "status": "healthy",
  "redis": "connected",
  "memory_usage": "2.1MB"
}
```

## 📈 Key Metrics to Monitor

### 1. Application Metrics
- **Response Time**: < 500ms for health checks
- **Uptime**: 99.9% target
- **Error Rate**: < 1%
- **Memory Usage**: < 80% of container limit
- **CPU Usage**: < 70% of container limit

### 2. Business Metrics
- **Active Domains**: Number of monitored domains
- **SSL Checks**: Successful checks per hour
- **Alert Delivery**: Success rate of notifications
- **API Calls**: Requests per minute
- **Stripe Events**: Successful webhook processing

### 3. Infrastructure Metrics
- **Database Connections**: Active connections
- **Redis Memory**: Cache hit ratio
- **Queue Length**: Pending Celery tasks
- **Log Errors**: Error frequency

## 🔍 Log Monitoring

### Render.com Logs
```bash
# View real-time logs
# Go to Render Dashboard → Your Service → Logs tab

# Key log patterns to watch:
- "Application startup complete" ✅
- "Database connected" ✅
- "Redis connected" ✅
- "ERROR" ❌
- "CRITICAL" ❌
- "SSL check failed" ⚠️
- "Stripe webhook failed" ❌
```

### Application Logs
```bash
# Log levels in production:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failed operations
- CRITICAL: System failures

# Log rotation: Automatic in Render
# Retention: 7 days (free tier)
```

## 🚨 Alert Thresholds

### Critical Alerts (Immediate Action)
- Service down > 2 minutes
- Database connection lost
- Redis connection lost
- SSL certificate expired
- Stripe webhook failures > 5%

### Warning Alerts (Monitor)
- Response time > 1 second
- Memory usage > 80%
- Error rate > 2%
- SSL expiry < 7 days
- Queue length > 100 tasks

### Info Alerts (Log Only)
- New domain added
- SSL check completed
- Payment processed
- User registered

## 📱 Notification Channels

### 1. Telegram Bot
```bash
# Test Telegram notifications
curl -X POST https://ssl-monitor-backend.onrender.com/test/telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "Test alert from monitoring system"}'
```

### 2. Email Alerts
```bash
# Test email notifications
curl -X POST https://ssl-monitor-backend.onrender.com/test/email \
  -H "Content-Type: application/json" \
  -d '{"email": "vla.maidaniuk@gmail.com", "message": "Test email alert"}'
```

### 3. Webhook Alerts
```bash
# Test webhook notifications
curl -X POST https://ssl-monitor-backend.onrender.com/test/webhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-webhook.com/alerts", "message": "Test webhook"}'
```

## 🛠️ Monitoring Tools

### Free Options
1. **Render Dashboard**: Built-in monitoring
2. **UptimeRobot**: Free uptime monitoring
3. **Pingdom**: Basic monitoring
4. **StatusCake**: Free tier available

### Setup UptimeRobot (Recommended)
1. Go to: https://uptimerobot.com
2. Create free account
3. Add monitor:
   - URL: `https://ssl-monitor-backend.onrender.com/health`
   - Type: HTTP(s)
   - Interval: 5 minutes
   - Alert contacts: Email + Telegram

### Custom Monitoring Script
```bash
#!/bin/bash
# monitor.sh - Simple health check script

URL="https://ssl-monitor-backend.onrender.com/health"
LOG_FILE="/tmp/ssl-monitor-health.log"

# Check health
response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json "$URL")
http_code="${response: -3}"

# Log result
timestamp=$(date -Iseconds)
if [ "$http_code" = "200" ]; then
    echo "$timestamp - HEALTHY" >> "$LOG_FILE"
else
    echo "$timestamp - UNHEALTHY (HTTP $http_code)" >> "$LOG_FILE"
    # Send alert
    curl -X POST https://ssl-monitor-backend.onrender.com/alerts \
      -H "Content-Type: application/json" \
      -d '{"type": "health_check_failed", "http_code": "'$http_code'"}'
fi
```

## 📊 Performance Monitoring

### Response Time Monitoring
```bash
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s https://ssl-monitor-backend.onrender.com/health

# curl-format.txt content:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                      ----------\n
#           time_total:  %{time_total}\n
```

### Load Testing
```bash
# Simple load test with curl
for i in {1..10}; do
  curl -s https://ssl-monitor-backend.onrender.com/health &
done
wait

# Check for errors in logs
```

## 🔧 Troubleshooting Commands

### Check Service Status
```bash
# Render service health
curl https://ssl-monitor-backend.onrender.com/health

# Database connectivity
curl https://ssl-monitor-backend.onrender.com/health/database

# Redis connectivity  
curl https://ssl-monitor-backend.onrender.com/health/redis
```

### Check Logs
```bash
# View recent logs (if you have Render CLI)
render logs ssl-monitor-backend --tail

# Or check in Render Dashboard → Logs tab
```

### Test SSL Monitoring
```bash
# Add test domain
curl -X POST https://ssl-monitor-backend.onrender.com/domains/ \
  -H "Content-Type: application/json" \
  -d '{"name": "google.com", "alert_threshold_days": 30}'

# Check SSL status
curl https://ssl-monitor-backend.onrender.com/domains/1/ssl-status
```

### Test Stripe Integration
```bash
# Test billing plans
curl https://ssl-monitor-backend.onrender.com/billing/plans

# Test checkout session
curl -X POST https://ssl-monitor-backend.onrender.com/billing/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "plan": "professional"}'
```

## 📋 Daily Monitoring Checklist

### Morning (9 AM)
- [ ] Check service health
- [ ] Review overnight logs
- [ ] Check SSL expiry alerts
- [ ] Verify payment processing
- [ ] Review error rates

### Evening (6 PM)
- [ ] Check daily metrics
- [ ] Review user registrations
- [ ] Check support emails
- [ ] Verify backup systems
- [ ] Plan tomorrow's tasks

### Weekly (Monday)
- [ ] Performance review
- [ ] Capacity planning
- [ ] Security updates
- [ ] Backup verification
- [ ] User feedback review

## 🚀 Scaling Indicators

### When to Scale Up
- Response time > 2 seconds consistently
- Memory usage > 90%
- CPU usage > 80%
- Database connections > 80% of limit
- Queue length > 500 tasks

### Scaling Options
1. **Render Upgrade**: Move to paid plan
2. **Database**: Add read replicas
3. **Redis**: Upgrade to paid tier
4. **CDN**: Add Cloudflare Pro
5. **Monitoring**: Add Sentry/DataDog

---

## 📞 Emergency Contacts

- **Developer**: vla.maidaniuk@gmail.com
- **Phone**: +420 721 579 603
- **Render Support**: https://render.com/support
- **Stripe Support**: https://support.stripe.com
- **Cloudflare Support**: https://dash.cloudflare.com/support
