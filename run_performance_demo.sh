#!/bin/bash
# Run performance demo using RKLLM server infrastructure

set -e

MODEL_PATH="/home/ubuntu/rk_llm_chat/Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
WORKSHOP_PATH="/home/ubuntu/rk_llm_chat"
PLATFORM="rk3588"
SERVER_DIR="/home/ubuntu/rk_llm_chat/rknn-llm/examples/rkllm_server_demo"

echo "=========================================="
echo "RKLLM Performance Demo"
echo "=========================================="
echo ""

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model file not found at $MODEL_PATH"
    exit 1
fi

echo "Model: $MODEL_PATH"
echo "Platform: $PLATFORM"
echo ""

# Change to server demo directory
cd "$SERVER_DIR"

# Install required Python package for performance testing
source "$WORKSHOP_PATH/.venv/bin/activate"
pip install -q requests 2>/dev/null || true

# Start Flask server in background
echo "Starting RKLLM Flask server..."
./build_rkllm_server_flask.sh \
  --workshop "$WORKSHOP_PATH" \
  --model_path "$MODEL_PATH" \
  --platform "$PLATFORM" > /tmp/rkllm_server.log 2>&1 &

SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
echo "Waiting for server to initialize..."
sleep 10

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null; then
    echo "Error: Server failed to start"
    cat /tmp/rkllm_server.log
    exit 1
fi

echo "Server started successfully"
echo ""

# Run performance test
echo "=========================================="
echo "Running Performance Tests"
echo "=========================================="
echo ""

# Create a simple performance test script
cat > /tmp/perf_test.py << 'EOF'
import requests
import time
import json

server_url = 'http://127.0.0.1:8080/rkllm_chat'
session = requests.Session()

# Test prompts
prompts = [
    "What is artificial intelligence?",
    "Explain quantum computing in simple terms.",
    "Write a short story about a robot.",
]

print("Running performance tests...")
print("=" * 60)

total_tokens = 0
total_time = 0
test_count = 0

for i, prompt in enumerate(prompts, 1):
    print(f"\nTest {i}/{len(prompts)}")
    print(f"Prompt: {prompt}")

    start_time = time.time()

    try:
        response = session.post(
            server_url,
            json={
                "prompt": prompt,
                "is_streaming": False
            },
            timeout=60
        )

        end_time = time.time()
        elapsed = end_time - start_time

        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '')

            # Rough token count (words * 1.3)
            tokens = int(len(text.split()) * 1.3)
            tps = tokens / elapsed if elapsed > 0 else 0

            print(f"Response: {text[:100]}...")
            print(f"Tokens: ~{tokens}")
            print(f"Time: {elapsed:.2f}s")
            print(f"Tokens/second: {tps:.2f}")

            total_tokens += tokens
            total_time += elapsed
            test_count += 1
        else:
            print(f"Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    print("-" * 60)

if test_count > 0:
    avg_tps = total_tokens / total_time if total_time > 0 else 0
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total tests: {test_count}")
    print(f"Total tokens: {total_tokens}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average tokens/second: {avg_tps:.2f}")
    print("=" * 60)
else:
    print("\nNo successful tests completed")
EOF

python3 /tmp/perf_test.py

# Cleanup
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null || true
sleep 2

echo "Performance test complete!"
