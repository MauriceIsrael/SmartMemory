#!/bin/bash
# Unified script to start the SmartMemory Supervision Dashboard
# This starts both the backend (FastAPI) and frontend (SvelteKit) in parallel

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}  SmartMemory Supervision Dashboard Launcher${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if venv exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    cd "$PROJECT_ROOT"
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[supervision]"
else
    echo -e "${GREEN}✓ Virtual environment found${NC}"
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  FastAPI not found. Installing dependencies...${NC}"
    pip install fastapi "uvicorn[standard]"
fi

if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}⚠️  npm not found. Please install Node.js and npm first.${NC}"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "$PROJECT_ROOT/src/supervision_frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not found. Installing...${NC}"
    cd "$PROJECT_ROOT/src/supervision_frontend"
    npm install
    cd "$PROJECT_ROOT"
fi

echo ""
echo -e "${GREEN}✓ All dependencies ready${NC}"
echo ""

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

# Trap to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Clean shutdown complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start backend
echo -e "${BLUE}🚀 Starting Backend (FastAPI on http://127.0.0.1:8000)...${NC}"
cd "$PROJECT_ROOT/src/supervision_backend"
"$PROJECT_ROOT/venv/bin/uvicorn" main:app --reload --port 8000 > /tmp/smartmemory_backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}   Backend PID: $BACKEND_PID${NC}"

# Wait a bit for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}🚀 Starting Frontend (SvelteKit on http://localhost:5173)...${NC}"
cd "$PROJECT_ROOT/src/supervision_frontend"
npm run dev -- --open > /tmp/smartmemory_frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}   Frontend PID: $FRONTEND_PID${NC}"

echo ""
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}✅ Dashboard is running!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "  📊 Dashboard: ${BLUE}http://localhost:5173${NC}"
echo -e "  🔧 Backend API: ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "  📋 API Docs: ${BLUE}http://127.0.0.1:8000/docs${NC}"
echo ""
echo -e "  📝 Backend logs: /tmp/smartmemory_backend.log"
echo -e "  📝 Frontend logs: /tmp/smartmemory_frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
