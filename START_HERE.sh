#!/bin/bash
# SSL Monitor Platform - Startup Script
# Run this script to start the entire platform

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       SSL Monitor Platform - Starting...                  ║"
echo "║       Professional SSL Certificate Monitoring              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -n "Checking Docker... "
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗${NC}"
    echo "Docker is not running. Starting Docker..."
    sudo systemctl start docker
    sleep 3
else
    echo -e "${GREEN}✓${NC}"
fi

# Check if docker-compose exists
echo -n "Checking docker-compose... "
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗${NC}"
    echo "docker-compose not found. Please install it first."
    exit 1
else
    echo -e "${GREEN}✓${NC}"
fi

# Start all services
echo ""
echo "Starting all services..."
echo "This may take a few minutes on first run..."
echo ""

sudo docker-compose up -d --build

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 15

# Check service health
echo ""
echo "Checking service health..."
echo ""

# Check Backend
echo -n "Backend API (port 8000)... "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Check Frontend
echo -n "Frontend Dashboard (port 80)... "
if curl -s http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Check PostgreSQL
echo -n "PostgreSQL Database... "
if sudo docker-compose exec -T postgres pg_isready -U ssluser > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ready${NC}"
else
    echo -e "${RED}✗ Not ready${NC}"
fi

# Check Redis
echo -n "Redis Cache... "
if sudo docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ready${NC}"
else
    echo -e "${RED}✗ Not ready${NC}"
fi

# Display access information
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 SYSTEM READY!                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Access your SSL Monitor Platform:"
echo ""
echo "  📊 Dashboard:        http://localhost"
echo "  📄 API Docs:         http://localhost:8000/docs"
echo "  🔍 ReDoc:            http://localhost:8000/redoc"
echo "  ❤️  Health Check:     http://localhost:8000/health"
echo "  💰 Landing Page:     http://localhost/landing.html"
echo ""
echo "Quick Commands:"
echo ""
echo "  View logs:           sudo docker-compose logs -f"
echo "  Stop services:       sudo docker-compose stop"
echo "  Restart services:    sudo docker-compose restart"
echo "  View status:         sudo docker-compose ps"
echo ""
echo "Documentation:"
echo ""
echo "  📖 Full Guide:       cat README.md"
echo "  🚀 Quick Start:      cat QUICKSTART.md"
echo "  ✅ Project Status:   cat PROJECT_COMPLETE.md"
echo ""
echo "Test the API:"
echo ""
echo "  curl http://localhost:8000/domains/"
echo "  curl -X POST http://localhost:8000/domains/1/check"
echo ""
echo "Happy monitoring! 🛡️"
echo ""

