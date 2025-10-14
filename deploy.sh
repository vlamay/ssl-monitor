#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║       🚀 SSL Monitor Pro - Production Deploy                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if all required files exist
echo "🔍 Checking required files..."
required_files=(
    "render.yaml"
    "backend/requirements.txt"
    "backend/app/main.py"
    "backend/app/billing.py"
    "backend/services/stripe_manager.py"
    "frontend/index.html"
    "frontend/pricing.html"
)

all_present=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - MISSING"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo -e "${RED}❌ Some required files are missing!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All required files present${NC}"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git config user.email "vla.maidaniuk@gmail.com"
    git config user.name "SSL Monitor Team"
    echo -e "${GREEN}✓${NC} Git initialized"
else
    echo -e "${GREEN}✓${NC} Git already initialized"
fi

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    echo "📝 Committing changes..."
    git add .
    git commit -m "🚀 Production Release: SSL Monitor Pro v1.0

Features:
- Complete SSL monitoring platform
- Stripe payment integration (€19/€49/€149 plans)
- Professional dashboard and pricing pages
- Email marketing automation
- Telegram/Slack notifications
- Referral program (10% + 20% commission)
- Ready for €1000 MRR

Tech Stack:
- Backend: FastAPI + PostgreSQL + Redis
- Workers: Celery + Celery Beat
- Payments: Stripe
- Deployment: Docker + Render.com

Status: Production Ready ✅"
    echo -e "${GREEN}✓${NC} Changes committed"
else
    echo -e "${YELLOW}ℹ${NC} No uncommitted changes"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ READY FOR PRODUCTION DEPLOY                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Create GitHub Repository:"
echo "   → Go to https://github.com/new"
echo "   → Name: ssl-monitor"
echo "   → Visibility: Public"
echo "   → Click 'Create repository'"
echo ""
echo "2️⃣  Push to GitHub:"
echo "   Run these commands (replace YOUR_USERNAME):"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/ssl-monitor.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣  Deploy on Render.com:"
echo "   → Go to https://render.com"
echo "   → Sign up with GitHub"
echo "   → Click 'New +' → 'Web Service'"
echo "   → Select your ssl-monitor repository"
echo "   → Render will auto-detect render.yaml"
echo "   → Click 'Apply' to deploy all services"
echo ""
echo "4️⃣  Set Environment Variables (in Render dashboard):"
echo "   → TELEGRAM_BOT_TOKEN (optional)"
echo "   → TELEGRAM_CHAT_ID (optional)"
echo "   → STRIPE_WEBHOOK_SECRET (from Stripe)"
echo ""
echo "⏰ Deployment time: 15-20 minutes"
echo "💰 Monthly cost: €0 (Free tier)"
echo ""
echo "🔗 Your live URL will be:"
echo "   https://ssl-monitor-backend.onrender.com"
echo ""
echo "📚 Full instructions: RENDER_DEPLOY_INSTRUCTIONS.md"
echo ""
echo "🎯 After deploy:"
echo "   • Share on LinkedIn"
echo "   • Post on Reddit"
echo "   • Email 10 potential customers"
echo "   • Get first paying customer! 💰"
echo ""
echo "Good luck! 🚀"

