#!/bin/bash
echo "🔍 Testing Backend Health..."
echo "================================"
echo ""

BACKEND_URL="https://ssl-monitor-api.onrender.com"

echo "1️⃣ Health Check:"
echo "   URL: $BACKEND_URL/health"
curl -s "$BACKEND_URL/health" | python3 -m json.tool || echo "❌ Failed to parse JSON"
echo ""

echo "2️⃣ API Root:"
echo "   URL: $BACKEND_URL/"
curl -s "$BACKEND_URL/" | python3 -m json.tool || echo "❌ Failed"
echo ""

echo "3️⃣ API Docs:"
echo "   URL: $BACKEND_URL/docs"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
echo "   Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ API Docs accessible"
else
    echo "   ❌ API Docs not accessible"
fi
echo ""

echo "4️⃣ CORS Check:"
echo "   Testing CORS headers for cloudsre.xyz..."
curl -s -I -H "Origin: https://cloudsre.xyz" "$BACKEND_URL/health" | grep -i "access-control" || echo "   ⚠️  No CORS headers (may need to add in backend)"
echo ""

echo "5️⃣ Statistics Endpoint:"
echo "   URL: $BACKEND_URL/statistics"
curl -s "$BACKEND_URL/statistics" | python3 -m json.tool || echo "❌ Failed"
echo ""

echo "6️⃣ Billing Plans:"
echo "   URL: $BACKEND_URL/billing/plans"
curl -s "$BACKEND_URL/billing/plans" | python3 -m json.tool || echo "❌ Failed"
echo ""

echo "================================"
echo "✅ Backend health check complete!"
echo ""
echo "🔗 URLs to test in browser:"
echo "   - API Docs: $BACKEND_URL/docs"
echo "   - Health: $BACKEND_URL/health"
echo "   - Stats: $BACKEND_URL/statistics"

