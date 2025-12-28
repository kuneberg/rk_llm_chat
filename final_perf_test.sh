#!/bin/bash
# Final performance test with multiple prompts

set -e

MODEL_PATH="/home/ubuntu/rk_llm_chat/Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
SERVER_DIR="/home/ubuntu/rk_llm_chat/rknn-llm/examples/rkllm_server_demo/rkllm_server"

echo "======================================================================"
echo "RKLLM Performance Test - Final Results"
echo "======================================================================"
echo "Model: Qwen3-4B (RKLLM Toolkit 1.2.1)"
echo "Runtime: v1.2.1b1"
echo "Platform: RK3588"
echo ""

cd "$SERVER_DIR"
source /home/ubuntu/rk_llm_chat/.venv/bin/activate

# Start server
echo "Starting RKLLM server..."
python3 flask_server.py \
  --rkllm_model_path "$MODEL_PATH" \
  --target_platform rk3588 > /tmp/server_final.log 2>&1 &

SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for initialization
sleep 20

# Test prompts
prompts=(
  "What is AI?"
  "Explain deep learning."
  "What are neural networks?"
)

total_tokens=0
total_time=0
count=0

echo ""
echo "Running performance tests..."
echo "----------------------------------------------------------------------"

for i in "${!prompts[@]}"; do
    prompt="${prompts[$i]}"
    test_num=$((i + 1))

    echo ""
    echo "Test $test_num/${#prompts[@]}: \"$prompt\""

    START=$(date +%s.%N)

    RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/rkllm_chat \
      -H "Content-Type: application/json" \
      -d "{\"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}], \"stream\": false}")

    END=$(date +%s.%N)
    ELAPSED=$(echo "$END - $START" | bc)

    # Extract and measure
    TEXT=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null || echo "")

    if [ -n "$TEXT" ]; then
        WORDS=$(echo "$TEXT" | wc -w)
        TOKENS=$(echo "$WORDS * 1.3" | bc | cut -d. -f1)
        TPS=$(echo "scale=2; $TOKENS / $ELAPSED" | bc)

        echo "Response length: $(echo "$TEXT" | wc -c) characters"
        echo "Tokens: ~$TOKENS"
        echo "Time: ${ELAPSED}s"
        echo "Tokens/second: $TPS"

        total_tokens=$((total_tokens + TOKENS))
        total_time=$(echo "$total_time + $ELAPSED" | bc)
        count=$((count + 1))
    else
        echo "Error: No response text"
    fi

    echo "----------------------------------------------------------------------"
done

# Calculate averages
if [ $count -gt 0 ]; then
    avg_tps=$(echo "scale=2; $total_tokens / $total_time" | bc)

    echo ""
    echo "======================================================================"
    echo "PERFORMANCE SUMMARY"
    echo "======================================================================"
    echo "Tests completed: $count/${#prompts[@]}"
    echo "Total tokens generated: ~$total_tokens"
    echo "Total time: ${total_time}s"
    echo "AVERAGE TOKENS/SECOND: $avg_tps"
    echo "======================================================================"
fi

# Cleanup
kill $SERVER_PID 2>/dev/null
echo ""
echo "Test complete!"
