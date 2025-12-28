#!/bin/bash
# Run RKLLM performance measurement

set -e

DEMO_DIR="/home/ubuntu/rk_llm_chat"

echo "=========================================="
echo "RKLLM Performance Test"
echo "=========================================="
echo ""

cd "$DEMO_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install requests if not already installed
pip install -q requests 2>/dev/null || true

# Run performance measurement
python3 measure_performance.py

exitcode=$?

# Ensure cleanup
pkill -f flask_server.py 2>/dev/null || true

exit $exitcode
