#!/bin/bash
# Quick performance test with the compatible model

set -e

MODEL_PATH="/home/ubuntu/rk_llm_chat/Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
SERVER_DIR="/home/ubuntu/rk_llm_chat/rknn-llm/examples/rkllm_server_demo/rkllm_server"

echo "Starting server..."
cd "$SERVER_DIR"
source /home/ubuntu/rk_llm_chat/.venv/bin/activate

# Start server in background
python3 flask_server.py \
  --rkllm_model_path "$MODEL_PATH" \
  --target_platform rk3588 > /tmp/server_output.log 2>&1 &

SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to initialize
echo "Waiting for server..."
sleep 15

# Test with curl
echo ""
echo "Testing inference..."
START=$(date +%s.%N)

RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/rkllm_chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is 2+2?"}], "stream": false}')

END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)

echo "Response: $RESPONSE"
echo ""
echo "Time: ${ELAPSED}s"

# Extract text and count tokens
TEXT=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null || echo "")

if [ -n "$TEXT" ]; then
    WORDS=$(echo "$TEXT" | wc -w)
    TOKENS=$(echo "$WORDS * 1.3" | bc | cut -d. -f1)
    TPS=$(echo "scale=2; $TOKENS / $ELAPSED" | bc)

    echo "Text: $TEXT"
    echo "Tokens: ~$TOKENS"
    echo "Tokens/second: $TPS"
fi

# Cleanup
kill $SERVER_PID 2>/dev/null
echo ""
echo "Done!"
