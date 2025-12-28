#!/bin/bash
# Start RKLLM chat server in the background

set -e

MODEL_PATH="/home/ubuntu/rk_llm_chat/Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
SERVER_DIR="/home/ubuntu/rk_llm_chat/rknn-llm/examples/rkllm_server_demo/rkllm_server"
LOG_FILE="/home/ubuntu/rk_llm_chat/chat_server.log"
PID_FILE="/home/ubuntu/rk_llm_chat/chat_server.pid"

echo "=========================================="
echo "Starting RKLLM Chat Server"
echo "=========================================="
echo ""

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Server is already running (PID: $OLD_PID)"
        echo "To stop it, run: bash stop_chat_server.sh"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model file not found: $MODEL_PATH"
    exit 1
fi

echo "Model: $MODEL_PATH"
echo "Log file: $LOG_FILE"
echo ""

# Start server
cd "$SERVER_DIR"
source /home/ubuntu/rk_llm_chat/.venv/bin/activate

echo "Initializing server (this may take 15-20 seconds)..."

nohup python3 flask_server.py \
    --rkllm_model_path "$MODEL_PATH" \
    --target_platform rk3588 \
    > "$LOG_FILE" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

echo "Server started with PID: $SERVER_PID"
echo ""

# Wait for server to initialize
echo -n "Waiting for server to be ready"
for i in {1..20}; do
    sleep 1
    echo -n "."
    if curl -s http://127.0.0.1:8080/ > /dev/null 2>&1; then
        echo ""
        echo ""
        echo "✓ Server is ready!"
        echo ""
        echo "To start chatting, run:"
        echo "  bash start_console_chat.sh"
        echo ""
        echo "To stop the server, run:"
        echo "  bash stop_chat_server.sh"
        echo ""
        exit 0
    fi
done

echo ""
echo ""
echo "✓ Server started (may still be initializing)"
echo ""
echo "To check server status, view the log:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To start chatting, run:"
echo "  bash start_console_chat.sh"
echo ""
