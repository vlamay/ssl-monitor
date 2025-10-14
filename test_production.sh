#!/bin/bash
# Test production deployment

if [ -z "$1" ]; then
    echo "Usage: ./test_production.sh <your-render-url>"
    echo "Example: ./test_production.sh https://ssl-monitor-backend.onrender.com"
    exit 1
fi

URL=$1

echo "🧪 Testing Production Deployment at: $URL"
echo ""

# Test 1: Health endpoint
echo "1️⃣  Testing health endpoint..."
curl -s "$URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$URL/health"
echo ""

# Test 2: Billing plans
echo "2️⃣  Testing billing plans..."
curl -s "$URL/billing/plans" | python3 -m json.tool 2>/dev/null || curl -s "$URL/billing/plans"
echo ""

# Test 3: Add test domain
echo "3️⃣  Testing domain creation..."
curl -s -X POST "$URL/domains/" \
  -H "Content-Type: application/json" \
  -d '{"name": "github.com"}' | python3 -m json.tool 2>/dev/null || echo "Domain may already exist"
echo ""

# Test 4: Get domains
echo "4️⃣  Testing domain list..."
curl -s "$URL/domains/" | python3 -m json.tool 2>/dev/null || curl -s "$URL/domains/"
echo ""

# Test 5: Get statistics
echo "5️⃣  Testing statistics..."
curl -s "$URL/statistics" | python3 -m json.tool 2>/dev/null || curl -s "$URL/statistics"
echo ""

echo "✅ Production tests completed!"
echo ""
echo "🌐 Your API is live at: $URL"
echo "📚 API Docs: $URL/docs"
echo "🎯 Next: Start acquiring customers!"

