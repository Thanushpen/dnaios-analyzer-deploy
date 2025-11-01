#!/bin/bash

# DNAiOS Analyzer Quick Start Script
# This script sets up and runs the analyzer locally

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🧬 DNAiOS Architecture Analyzer - Quick Start           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python installation
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip found${NC}"

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Start backend
echo ""
echo "🚀 Starting backend server..."
echo -e "${YELLOW}Backend will run on http://localhost:5001${NC}"
echo ""
python analyzer.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running!${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend
echo ""
echo "🎨 Starting frontend server..."
cd ../frontend
echo -e "${YELLOW}Frontend will run on http://localhost:8000${NC}"
echo ""
python3 -m http.server 8000 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 ALL SET!                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Backend:  http://localhost:5001"
echo "Frontend: http://localhost:8000"
echo ""
echo "Open your browser and visit: http://localhost:8000"
echo ""
echo "To stop the servers, press Ctrl+C"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo 'Done!'; exit 0" INT

# Keep script running
wait
