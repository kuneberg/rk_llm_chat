#!/bin/bash
# Start console chat interface

set -e

# Check if server is running
if ! curl -s http://127.0.0.1:8080/ > /dev/null 2>&1; then
    echo "=========================================="
    echo "RKLLM server is not running!"
    echo "=========================================="
    echo ""
    echo "Please start the server first:"
    echo "  bash start_chat_server.sh"
    echo ""
    echo "Then run this script again to start chatting."
    exit 1
fi

# Activate virtual environment and start chat
cd /home/ubuntu/rk_llm_chat
source .venv/bin/activate

python3 console_chat.py
