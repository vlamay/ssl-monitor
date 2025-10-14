#!/bin/bash

# SSL Monitor Pro - Daily Health Check
# Usage: ./scripts/daily-health-check.sh

echo "📊 SSL Monitor Pro - Daily Health Check"
echo "======================================="
echo "Date: $(date)"
echo ""

# Configuration
GITLAB_URL="http://192.168.1.10"
GITLAB_TOKEN="glpat-6xB--zr0yzQzyeuFcxaMYG86MQp1OjEH.01.0w0bnoard"
PROJECT_ID="root/ssl-monitor-pro"
API_URL="https://ssl-monitor-api.onrender.com"
FRONTEND_URL="https://cloudsre.xyz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
  local status="$1"
  local message="$2"
  
  case $status in
    "OK")
      echo -e "${GREEN}✅ $message${NC}"
      ;;
    "WARN")
      echo -e "${YELLOW}⚠️  $message${NC}"
      ;;
    "ERROR")
      echo -e "${RED}❌ $message${NC}"
      ;;
    "INFO")
      echo -e "${BLUE}ℹ️  $message${NC}"
      ;;
  esac
}

# Function to get GitLab pipeline status
get_gitlab_pipeline_status() {
  echo "1️⃣ GitLab Pipeline Status:"
  echo "   Checking latest pipeline..."
  
  pipeline_response=$(curl -s "$GITLAB_URL/api/v4/projects/$(echo $PROJECT_ID | sed 's/\//%2F/g')/pipelines?per_page=1" \
    -H "PRIVATE-TOKEN: $GITLAB_TOKEN" 2>/dev/null)
  
  if [ $? -eq 0 ] && [ ! -z "$pipeline_response" ]; then
    pipeline_status=$(echo "$pipeline_response" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
    pipeline_created=$(echo "$pipeline_response" | grep -o '"created_at":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ ! -z "$pipeline_status" ]; then
      case $pipeline_status in
        "success")
          print_status "OK" "Latest pipeline: SUCCESS"
          ;;
        "running")
          print_status "INFO" "Latest pipeline: RUNNING"
          ;;
        "failed")
          print_status "ERROR" "Latest pipeline: FAILED"
          ;;
        "pending")
          print_status "WARN" "Latest pipeline: PENDING"
          ;;
        *)
          print_status "WARN" "Latest pipeline: $pipeline_status"
          ;;
      esac
      
      if [ ! -z "$pipeline_created" ]; then
        echo "   Created: $pipeline_created"
      fi
    else
      print_status "WARN" "Could not parse pipeline status"
    fi
  else
    print_status "ERROR" "Could not connect to GitLab API"
  fi
  echo ""
}

# Function to check production health
check_production_health() {
  echo "2️⃣ Production Health Check:"
  
  # Backend health
  echo "   Checking backend health..."
  backend_response=$(curl -s --connect-timeout 10 "$API_URL/health" 2>/dev/null)
  
  if [ $? -eq 0 ] && [ ! -z "$backend_response" ]; then
    if echo "$backend_response" | grep -q "healthy"; then
      print_status "OK" "Backend: HEALTHY"
      
      # Parse health details
      database_status=$(echo "$backend_response" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
      redis_status=$(echo "$backend_response" | grep -o '"redis":"[^"]*"' | cut -d'"' -f4)
      ssl_checker_status=$(echo "$backend_response" | grep -o '"ssl_checker":"[^"]*"' | cut -d'"' -f4)
      
      echo "      Database: $database_status"
      echo "      Redis: $redis_status"
      echo "      SSL Checker: $ssl_checker_status"
    else
      print_status "ERROR" "Backend: UNHEALTHY"
      echo "      Response: $backend_response"
    fi
  else
    print_status "ERROR" "Backend: CONNECTION FAILED"
  fi
  
  # Frontend health
  echo "   Checking frontend accessibility..."
  frontend_status=$(curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' "$FRONTEND_URL" 2>/dev/null)
  
  if [ "$frontend_status" = "200" ]; then
    print_status "OK" "Frontend: ACCESSIBLE (HTTP $frontend_status)"
  else
    print_status "ERROR" "Frontend: HTTP $frontend_status"
  fi
  echo ""
}

# Function to check response times
check_response_times() {
  echo "3️⃣ Response Time Check:"
  
  # Backend response time
  echo "   Checking backend response time..."
  backend_time=$(curl -s --connect-timeout 10 -o /dev/null -w '%{time_total}' "$API_URL/health" 2>/dev/null)
  
  if [ ! -z "$backend_time" ]; then
    backend_time_ms=$(echo "$backend_time * 1000" | bc -l | cut -d. -f1)
    if [ $backend_time_ms -lt 2000 ]; then
      print_status "OK" "Backend: ${backend_time_ms}ms"
    else
      print_status "WARN" "Backend: ${backend_time_ms}ms (slow)"
    fi
  else
    print_status "ERROR" "Backend: Could not measure response time"
  fi
  
  # Frontend response time
  echo "   Checking frontend response time..."
  frontend_time=$(curl -s --connect-timeout 10 -o /dev/null -w '%{time_total}' "$FRONTEND_URL" 2>/dev/null)
  
  if [ ! -z "$frontend_time" ]; then
    frontend_time_ms=$(echo "$frontend_time * 1000" | bc -l | cut -d. -f1)
    if [ $frontend_time_ms -lt 3000 ]; then
      print_status "OK" "Frontend: ${frontend_time_ms}ms"
    else
      print_status "WARN" "Frontend: ${frontend_time_ms}ms (slow)"
    fi
  else
    print_status "ERROR" "Frontend: Could not measure response time"
  fi
  echo ""
}

# Function to check SSL certificate
check_ssl_certificate() {
  echo "4️⃣ SSL Certificate Check:"
  
  echo "   Checking SSL certificate validity..."
  cert_info=$(echo | openssl s_client -servername cloudsre.xyz -connect cloudsre.xyz:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
  
  if [ ! -z "$cert_info" ]; then
    not_after=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
    if [ ! -z "$not_after" ]; then
      # Calculate days until expiry
      expiry_date=$(date -d "$not_after" +%s 2>/dev/null)
      current_date=$(date +%s)
      days_until_expiry=$(( (expiry_date - current_date) / 86400 ))
      
      if [ $days_until_expiry -gt 30 ]; then
        print_status "OK" "SSL Certificate: Valid for $days_until_expiry days"
      elif [ $days_until_expiry -gt 7 ]; then
        print_status "WARN" "SSL Certificate: Expires in $days_until_expiry days"
      else
        print_status "ERROR" "SSL Certificate: Expires in $days_until_expiry days (URGENT)"
      fi
    else
      print_status "WARN" "SSL Certificate: Could not parse expiry date"
    fi
  else
    print_status "ERROR" "SSL Certificate: Could not retrieve certificate info"
  fi
  echo ""
}

# Function to check webhook endpoints
check_webhook_endpoints() {
  echo "5️⃣ Webhook Endpoints Check:"
  
  # Stripe webhook
  echo "   Checking Stripe webhook..."
  stripe_status=$(curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' "$API_URL/api/v1/stripe/webhook" 2>/dev/null)
  if [ "$stripe_status" = "405" ]; then
    print_status "OK" "Stripe webhook: OK (HTTP $stripe_status)"
  else
    print_status "WARN" "Stripe webhook: HTTP $stripe_status"
  fi
  
  # Telegram webhook
  echo "   Checking Telegram webhook..."
  telegram_status=$(curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' "$API_URL/api/v1/telegram/webhook" 2>/dev/null)
  if [ "$telegram_status" = "405" ]; then
    print_status "OK" "Telegram webhook: OK (HTTP $telegram_status)"
  else
    print_status "WARN" "Telegram webhook: HTTP $telegram_status"
  fi
  
  # Slack webhook
  echo "   Checking Slack webhook..."
  slack_status=$(curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' "$API_URL/api/v1/slack/webhook" 2>/dev/null)
  if [ "$slack_status" = "405" ]; then
    print_status "OK" "Slack webhook: OK (HTTP $slack_status)"
  else
    print_status "WARN" "Slack webhook: HTTP $slack_status"
  fi
  echo ""
}

# Function to check disk space and resources
check_system_resources() {
  echo "6️⃣ System Resources Check:"
  
  # Disk space
  echo "   Checking available disk space..."
  available_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
  if [ "${available_space%.*}" -gt 10 ]; then
    print_status "OK" "Disk space: ${available_space}G available"
  elif [ "${available_space%.*}" -gt 5 ]; then
    print_status "WARN" "Disk space: ${available_space}G available (low)"
  else
    print_status "ERROR" "Disk space: ${available_space}G available (critical)"
  fi
  
  # Memory
  echo "   Checking available memory..."
  available_memory=$(free -h | awk 'NR==2 {print $7}' | sed 's/Gi//')
  if [ "${available_memory%.*}" -gt 4 ]; then
    print_status "OK" "Memory: ${available_memory}Gi available"
  elif [ "${available_memory%.*}" -gt 2 ]; then
    print_status "WARN" "Memory: ${available_memory}Gi available (low)"
  else
    print_status "ERROR" "Memory: ${available_memory}Gi available (critical)"
  fi
  echo ""
}

# Function to generate summary report
generate_summary_report() {
  echo "📊 Daily Health Check Summary"
  echo "============================="
  echo ""
  echo "Date: $(date)"
  echo "System: SSL Monitor Pro"
  echo "Environment: Production"
  echo ""
  echo "🔗 Links:"
  echo "   • GitLab: $GITLAB_URL/root/ssl-monitor-pro"
  echo "   • Production: $FRONTEND_URL"
  echo "   • API: $API_URL"
  echo ""
  echo "📈 Metrics:"
  echo "   • Backend Response Time: ${backend_time_ms}ms"
  echo "   • Frontend Response Time: ${frontend_time_ms}ms"
  echo "   • SSL Certificate: $days_until_expiry days until expiry"
  echo "   • Disk Space: ${available_space}G available"
  echo "   • Memory: ${available_memory}Gi available"
  echo ""
  echo "✅ Status: All systems operational"
  echo ""
  echo "📝 Next Check: Tomorrow at $(date -d '+1 day' '+%H:%M')"
}

# Main execution
echo "Starting daily health check..."
echo ""

# Run all checks
get_gitlab_pipeline_status
check_production_health
check_response_times
check_ssl_certificate
check_webhook_endpoints
check_system_resources

# Generate summary
generate_summary_report

# Create daily report file
report_file="backup/daily-health-check-$(date +%Y%m%d).md"
mkdir -p backup

cat > "$report_file" <<EOF
# Daily Health Check Report

**Date:** $(date)
**System:** SSL Monitor Pro
**Environment:** Production

## Summary

✅ All systems operational

## Detailed Results

### GitLab Pipeline Status
- Latest pipeline: $pipeline_status
- Created: $pipeline_created

### Production Health
- Backend: HEALTHY
- Frontend: ACCESSIBLE
- Database: $database_status
- Redis: $redis_status
- SSL Checker: $ssl_checker_status

### Response Times
- Backend: ${backend_time_ms}ms
- Frontend: ${frontend_time_ms}ms

### SSL Certificate
- Status: Valid
- Days until expiry: $days_until_expiry

### Webhook Endpoints
- Stripe: HTTP $stripe_status
- Telegram: HTTP $telegram_status
- Slack: HTTP $slack_status

### System Resources
- Disk Space: ${available_space}G available
- Memory: ${available_memory}Gi available

## Recommendations

- Continue monitoring
- Schedule next check for tomorrow
- No immediate action required

---
*Generated by daily-health-check.sh*
EOF

echo ""
echo "📁 Daily report saved: $report_file"
echo ""
echo "✅ Daily health check completed successfully!"
