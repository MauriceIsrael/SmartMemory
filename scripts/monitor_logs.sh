#!/usr/bin/env bash
# Monitor SmartMemory MCP server logs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LOG_FILE="$PROJECT_ROOT/mcp_server.log"

echo "📊 SmartMemory MCP Server Log Monitor"
echo "======================================"
echo ""
echo "Log file: $LOG_FILE"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  Log file not found. The server may not have started yet."
    echo ""
    echo "To enable logging, update your ~/.gemini/settings.json:"
    echo ""
    echo '  "semantic-memory": {'
    echo '    "command": "/path/to/venv/bin/python",'
    echo '    "args": ["/path/to/src/server.py"],'
    echo '    "env": {'
    echo '      "PYTHONPATH": "/path/to/SmartMemory",'
    echo '      "LOG_FILE": "/path/to/SmartMemory/mcp_server.log"'
    echo '    }'
    echo '  }'
    echo ""
    echo "Or run the server manually with:"
    echo "  PYTHONPATH=. venv/bin/python src/server.py 2>&1 | tee mcp_server.log"
    exit 1
fi

echo "📖 Showing last 50 lines, then following new logs..."
echo "   Press Ctrl+C to stop"
echo ""

tail -n 50 -f "$LOG_FILE"
