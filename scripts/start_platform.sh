#!/bin/bash
# ============================================
# Gram Meter Platform - One-Click Startup
# ============================================
# This script starts all services:
# 1. Django Backend (port 8000)
# 2. Frontend User App (port 5173)
# 3. Admin Console (port 5174)
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "============================================"
echo "   🌾 Gram Meter Platform Startup"
echo "============================================"
echo -e "${NC}"

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}⚠️  Port $1 in use, stopping existing process...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to wait for port to be ready
wait_for_port() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if check_port $port; then
            echo -e "${GREEN}✅ $name is ready on port $port${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}❌ $name failed to start on port $port${NC}"
    return 1
}

# Clean up old processes
echo -e "${YELLOW}🧹 Cleaning up old processes...${NC}"
kill_port 8000
kill_port 5173
kill_port 5174

# Check Python virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"
echo ""

# Start Backend (Django)
echo -e "${YELLOW}1️⃣  Starting Django Backend...${NC}"
cd "$SCRIPT_DIR/backend"
python manage.py runserver 0.0.0.0:8000 > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"

# Start Frontend (Vite)
echo -e "${YELLOW}2️⃣  Starting Frontend (User App)...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   PID: $FRONTEND_PID"

# Start Admin Console
echo -e "${YELLOW}3️⃣  Starting Admin Console...${NC}"
cd "$SCRIPT_DIR/Admin console"
npm run dev -- --port 5174 > "$SCRIPT_DIR/logs/admin_console.log" 2>&1 &
ADMIN_PID=$!
echo "   PID: $ADMIN_PID"

# Wait for services to be ready
echo ""
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 3

wait_for_port 8000 "Django Backend"
wait_for_port 5173 "Frontend User App"
wait_for_port 5174 "Admin Console"

# Save PIDs to file for stop script
cd "$SCRIPT_DIR"
echo "$BACKEND_PID" > .pids/backend.pid
echo "$FRONTEND_PID" > .pids/frontend.pid
echo "$ADMIN_PID" > .pids/admin.pid

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   ✅ All Services Running!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "   ${BLUE}🌐 User App:${NC}      http://localhost:5173"
echo -e "   ${BLUE}🔧 Admin Console:${NC} http://localhost:5174"
echo -e "   ${BLUE}🖥️  Backend API:${NC}   http://localhost:8000/api/v1/"
echo ""
echo -e "${YELLOW}📋 Admin Login Credentials:${NC}"
echo -e "   Username: admin"
echo -e "   Password: admin123"
echo ""
echo -e "${YELLOW}📋 Test User Credentials:${NC}"
echo -e "   Phone: 9876543210 (farmer_ramesh)"
echo -e "   Phone: 9876543211 (farmer_priya)"
echo ""
echo -e "${BLUE}📁 Logs are available at:${NC}"
echo -e "   - logs/backend.log"
echo -e "   - logs/frontend.log"
echo -e "   - logs/admin_console.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running and handle Ctrl+C
trap 'echo -e "\n${RED}🛑 Stopping all services...${NC}"; kill $BACKEND_PID $FRONTEND_PID $ADMIN_PID 2>/dev/null; exit 0' INT TERM

# Wait for any process to exit
wait
