#!/bin/bash
# Run RKLLM demo using the official server infrastructure

set -e

MODEL_PATH="/home/ubuntu/rk_llm_chat/Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
WORKSHOP_PATH="/home/ubuntu/rk_llm_chat"
PLATFORM="rk3588"

echo "=========================================="
echo "RKLLM Demo Runner"
echo "=========================================="
echo ""

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model file not found at $MODEL_PATH"
    exit 1
fi

echo "Model: $MODEL_PATH"
echo "Platform: $PLATFORM"
echo "Workshop: $WORKSHOP_PATH"
echo ""

# Run simple demo first
echo "Running simple library check..."
cd "$WORKSHOP_PATH"
source .venv/bin/activate
python3 simple_demo.py
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "The RKLLM runtime is installed and ready."
echo ""
echo "To run inference demos:"
echo "1. Flask Server (HTTP API):"
echo "   cd rknn-llm/examples/rkllm_server_demo"
echo "   ./build_rkllm_server_flask.sh --workshop $WORKSHOP_PATH \\"
echo "     --model_path $MODEL_PATH \\"
echo "     --platform $PLATFORM"
echo ""
echo "2. Gradio Server (Web UI):"
echo "   cd rknn-llm/examples/rkllm_server_demo"
echo "   ./build_rkllm_server_gradio.sh --workshop $WORKSHOP_PATH \\"
echo "     --model_path $MODEL_PATH \\"
echo "     --platform $PLATFORM"
echo ""
