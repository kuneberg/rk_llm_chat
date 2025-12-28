#!/bin/bash
# Run standalone performance demo

set -e

DEMO_DIR="/home/ubuntu/rk_llm_chat"

echo "=========================================="
echo "RKLLM Performance Demo Runner"
echo "=========================================="
echo ""

cd "$DEMO_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run performance demo
python3 performance_demo.py

echo ""
echo "Performance test complete!"
