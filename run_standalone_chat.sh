#!/bin/bash
# Run standalone console chat with embedded model

set -e

SCRIPT_DIR="/home/ubuntu/rk_llm_chat"

echo "=========================================="
echo "RKLLM Standalone Console Chat"
echo "=========================================="
echo ""

cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run standalone chat
python3 standalone_console.py

echo ""
echo "Chat session ended."
