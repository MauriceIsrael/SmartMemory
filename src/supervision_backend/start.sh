#!/bin/bash
# Script to start the supervision backend with correct PYTHONPATH

# Set PYTHONPATH to include the project root
export PYTHONPATH=/home/momo/Antigravity/SmartMemory/src:/home/momo/Antigravity/SmartMemory:$PYTHONPATH

# Activate virtual environment
source venv/bin/activate

# Start uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
