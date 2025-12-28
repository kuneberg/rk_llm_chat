#!/bin/bash
# Stop RKLLM chat server

PID_FILE="/home/ubuntu/rk_llm_chat/chat_server.pid"

echo "Stopping RKLLM Chat Server..."

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        echo "Server stopped (PID: $PID)"
        rm -f "$PID_FILE"
    else
        echo "Server was not running"
        rm -f "$PID_FILE"
    fi
else
    echo "No PID file found"
    # Try to kill any flask_server.py process
    pkill -f flask_server.py && echo "Killed flask_server.py processes" || echo "No flask_server.py processes found"
fi
