#!/bin/bash
# ============================================
# Gram Meter Platform - Stop All Services
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}"
echo "============================================"
echo "   🛑 Stopping Gram Meter Platform"
echo "============================================"
echo -e "${NC}"

# Kill processes on ports
echo "Stopping Backend (port 8000)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✅ Backend stopped${NC}" || echo "Not running"

echo "Stopping Frontend (port 5173)..."
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✅ Frontend stopped${NC}" || echo "Not running"

echo "Stopping Admin Console (port 5174)..."
lsof -ti:5174 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✅ Admin Console stopped${NC}" || echo "Not running"

echo ""
echo -e "${GREEN}All services stopped!${NC}"
