#!/bin/bash
echo "🔍 SSL Monitor Pro - Production Verification"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check frontend
echo -n "🎨 Frontend (cloudsre.xyz): "
if curl -s -o /dev/null -w "%{http_code}" https://cloudsre.xyz | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check backend health
echo -n "🔧 Backend health: "
HEALTH=$(curl -s https://status.cloudsre.xyz/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check API docs
echo -n "📚 API docs: "
if curl -s -o /dev/null -w "%{http_code}" https://status.cloudsre.xyz/docs | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check statistics
echo -n "📊 Statistics endpoint: "
if curl -s https://status.cloudsre.xyz/statistics | grep -q "total_domains"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check billing plans
echo -n "💳 Billing plans: "
if curl -s https://status.cloudsre.xyz/billing/plans | grep -q "plans"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

echo ""
echo "🎯 Verification Complete!"
