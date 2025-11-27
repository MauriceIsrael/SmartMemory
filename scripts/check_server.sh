#!/bin/bash
# Helper script to check and clean up SmartMemory MCP server processes

echo "=== SmartMemory MCP Server Process Status ==="
echo

# Find all python processes running semantic_memory.server
PROCS=$(ps aux | grep '[s]emantic_memory.server' | awk '{print $2, $11, $12, $13, $14, $15}')

if [ -z "$PROCS" ]; then
    echo "✓ No SmartMemory server processes found"
else
    echo "⚠️  Found SmartMemory server processes:"
    echo "$PROCS" | while read line; do
        PID=$(echo $line | awk '{print $1}')
        CMD=$(echo $line | cut -d' ' -f2-)
        echo "  PID $PID: $CMD"
    done
    
    echo
    read -p "Kill these processes? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$PROCS" | awk '{print $1}' | xargs kill -SIGTERM
        echo "✓ Sent SIGTERM to processes"
        sleep 2
        
        # Check if any are still running
        STILL_RUNNING=$(ps aux | grep '[s]emantic_memory.server' | awk '{print $2}')
        if [ ! -z "$STILL_RUNNING" ]; then
            echo "⚠️  Some processes still running, sending SIGKILL..."
            echo "$STILL_RUNNING" | xargs kill -SIGKILL
            echo "✓ Processes killed"
        fi
    fi
fi

echo
echo "=== Log file status ==="
if [ -f /tmp/smartmemory.log ]; then
    SIZE=$(du -h /tmp/smartmemory.log | cut -f1)
    LINES=$(wc -l < /tmp/smartmemory.log)
    echo "  Log file: /tmp/smartmemory.log ($SIZE, $LINES lines)"
    echo "  Last 3 lines:"
    tail -3 /tmp/smartmemory.log | sed 's/^/    /'
else
    echo "  No log file found at /tmp/smartmemory.log"
fi
