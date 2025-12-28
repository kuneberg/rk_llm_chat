#!/bin/bash
# Run RKLLM model benchmark

set -e

SCRIPT_DIR="/home/ubuntu/rk_llm_chat"

echo "==========================================="
echo "RKLLM Model Benchmark"
echo "==========================================="
echo ""

cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run benchmark
python3 benchmark.py

echo ""
echo "Benchmark completed."
