#!/bin/bash
set -e

# Entrypoint script for SmartMemory Docker image
# Supports two modes:
# 1. MCP mode (default): stdin/stdout communication
# 2. Dashboard mode: web server on port 8080

if [ "$1" = "dashboard" ]; then
    echo "Starting SmartMemory in Dashboard mode (http://0.0.0.0:8080)"
    exec uvicorn src.dashboard.backend.main:app --host 0.0.0.0 --port 8080
else
    # MCP mode (default)
    exec python -m smart_memory.server
fi
