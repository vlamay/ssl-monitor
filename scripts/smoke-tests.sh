#!/bin/bash

# SSL Monitor Pro - Production Smoke Tests
# Usage: ./scripts/smoke-tests.sh

echo "🧪 Running SSL Monitor Pro Smoke Tests..."
echo "=========================================="
echo ""

API_URL="https://ssl-monitor-api.onrender.com"
FRONTEND_URL="https://cloudsre.xyz"
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
  local test_name="$1"
  local test_command="$2"
  local expected_result="$3"
  
  echo "🧪 Testing: $test_name"
  echo "   Command: $test_command"
  
  # Run the test command
  result=$(eval "$test_command" 2>&1)
  exit_code=$?
  
  if [ $exit_code -eq 0 ] && [[ "$result" == *"$expected_result"* ]]; then
    echo "   ✅ PASS"
    ((TESTS_PASSED++))
  else
    echo "   ❌ FAIL"
    echo "   Expected: $expected_result"
    echo "   Got: $result"
    ((TESTS_FAILED++))
  fi
  echo ""
}

# Test 1: Backend Health Check
run_test "Backend Health Check" \
  "curl -s $API_URL/health" \
  "healthy"

# Test 2: Backend API Documentation
run_test "API Documentation" \
  "curl -s -o /dev/null -w '%{http_code}' $API_URL/docs" \
  "200"

# Test 3: Frontend Homepage
run_test "Frontend Homepage" \
  "curl -s -o /dev/null -w '%{http_code}' $FRONTEND_URL" \
  "200"

# Test 4: Database Connection
run_test "Database Connection" \
  "curl -s $API_URL/health | grep -o '\"database\":\"connected\"'" \
  "database\":\"connected"

# Test 5: Redis Connection
run_test "Redis Connection" \
  "curl -s $API_URL/health | grep -o '\"redis\":\"error'" \
  "redis\":\"error"

# Test 6: Telegram Service
run_test "Telegram Service" \
  "curl -s $API_URL/health | grep -o '\"telegram\":\"connected'" \
  "telegram\":\"connected"

# Test 7: Stripe Webhook Endpoint
run_test "Stripe Webhook Endpoint" \
  "curl -s -o /dev/null -w '%{http_code}' $API_URL/api/v1/stripe/webhook" \
  "405"

# Test 8: Telegram Webhook Endpoint
run_test "Telegram Webhook Endpoint" \
  "curl -s -o /dev/null -w '%{http_code}' $API_URL/api/v1/telegram/webhook" \
  "405"

# Test 9: Slack Webhook Endpoint
run_test "Slack Webhook Endpoint" \
  "curl -s -o /dev/null -w '%{http_code}' $API_URL/api/v1/slack/webhook" \
  "405"

# Test 10: Frontend Static Assets
run_test "Frontend Static Assets" \
  "curl -s -o /dev/null -w '%{http_code}' $FRONTEND_URL/css/style.css" \
  "200"

# Test 11: API Response Time (should be < 2000ms)
echo "🧪 Testing: API Response Time"
response_time=$(curl -s -o /dev/null -w '%{time_total}' $API_URL/health)
response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)

if [ $response_time_ms -lt 2000 ]; then
  echo "   ✅ PASS (${response_time_ms}ms)"
  ((TESTS_PASSED++))
else
  echo "   ❌ FAIL (${response_time_ms}ms > 2000ms)"
  ((TESTS_FAILED++))
fi
echo ""

# Test 12: Frontend Response Time (should be < 3000ms)
echo "🧪 Testing: Frontend Response Time"
response_time=$(curl -s -o /dev/null -w '%{time_total}' $FRONTEND_URL)
response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)

if [ $response_time_ms -lt 3000 ]; then
  echo "   ✅ PASS (${response_time_ms}ms)"
  ((TESTS_PASSED++))
else
  echo "   ❌ FAIL (${response_time_ms}ms > 3000ms)"
  ((TESTS_FAILED++))
fi
echo ""

# Test 13: HTTPS Certificate
echo "🧪 Testing: HTTPS Certificate"
cert_check=$(echo | openssl s_client -servername cloudsre.xyz -connect cloudsre.xyz:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)

if [ ! -z "$cert_check" ]; then
  echo "   ✅ PASS (Valid SSL certificate)"
  ((TESTS_PASSED++))
else
  echo "   ❌ FAIL (Invalid or missing SSL certificate)"
  ((TESTS_FAILED++))
fi
echo ""

# Test 14: Database Migration Status
echo "🧪 Testing: Database Migration Status"
migration_status=$(curl -s $API_URL/health | grep -o '\"migrations\":\"ok\"')

if [ ! -z "$migration_status" ]; then
  echo "   ✅ PASS (Database migrations up to date)"
  ((TESTS_PASSED++))
else
  echo "   ❌ FAIL (Database migration issues)"
  ((TESTS_FAILED++))
fi
echo ""

# Summary
echo "=========================================="
echo "📊 SMOKE TESTS SUMMARY"
echo "=========================================="
echo "✅ Tests Passed: $TESTS_PASSED"
echo "❌ Tests Failed: $TESTS_FAILED"
echo "📈 Success Rate: $(( TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED) ))%"

if [ $TESTS_FAILED -eq 0 ]; then
  echo ""
  echo "🎉 ALL TESTS PASSED!"
  echo "✅ Production system is healthy"
  exit 0
else
  echo ""
  echo "⚠️  SOME TESTS FAILED!"
  echo "❌ Production system has issues"
  echo ""
  echo "🔧 Recommended actions:"
  echo "   1. Check Render.com logs"
  echo "   2. Verify environment variables"
  echo "   3. Check database connectivity"
  echo "   4. Review GitLab pipeline status"
  exit 1
fi
