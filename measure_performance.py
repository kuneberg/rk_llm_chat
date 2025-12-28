#!/usr/bin/env python3
"""
RKLLM Performance Measurement Tool
Uses the official Flask server and measures tokens/second
"""

import requests
import time
import json
import sys
import subprocess
import os
import signal

SERVER_URL = 'http://127.0.0.1:8080/rkllm_chat'
MODEL_PATH = "/home/ubuntu/rk_llm_chat/Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
PLATFORM = "rk3588"

# Test prompts
TEST_PROMPTS = [
    "What is artificial intelligence?",
    "Explain machine learning.",
    "What are neural networks?",
]

def wait_for_server(timeout=60):
    """Wait for server to be ready"""
    print("Waiting for server to start...", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get('http://127.0.0.1:8080/', timeout=2)
            print(" Ready!")
            return True
        except:
            print(".", end="", flush=True)
            time.sleep(2)
    print(" Timeout!")
    return False

def measure_performance():
    """Run performance tests"""
    print()
    print("=" * 70)
    print("RKLLM Performance Test")
    print("=" * 70)
    print()

    session = requests.Session()
    session.keep_alive = False

    total_tokens = 0
    total_time = 0
    test_count = 0

    for i, prompt in enumerate(TEST_PROMPTS, 1):
        print(f"Test {i}/{len(TEST_PROMPTS)}")
        print(f"Prompt: {prompt}")
        print()

        start_time = time.time()

        try:
            # Use the messages format expected by the server
            response = session.post(
                SERVER_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=120
            )

            end_time = time.time()
            elapsed = end_time - start_time

            if response.status_code == 200:
                result = response.json()

                # Debug: print raw response
                print(f"DEBUG: Response JSON: {json.dumps(result, indent=2)[:500]}")
                print()

                # Extract response text
                text = ""
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    text = content if content else result.get('response', '')
                else:
                    text = result.get('response', result.get('text', str(result)))

                # Estimate tokens (words * 1.3 is a common approximation)
                if text:
                    tokens = max(1, int(len(text.split()) * 1.3))
                else:
                    tokens = 0

                tps = tokens / elapsed if elapsed > 0 else 0

                print(f"Response: {text[:150]}..." if text else "Response: (empty)")
                print()
                print(f"Time: {elapsed:.2f}s")
                print(f"Estimated tokens: ~{tokens}")
                print(f"Tokens/second: {tps:.2f}")

                total_tokens += tokens
                total_time += elapsed
                test_count += 1
            else:
                print(f"Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        print("-" * 70)
        print()

    # Summary
    if test_count > 0:
        avg_tps = total_tokens / total_time if total_time > 0 else 0

        print("=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"Tests completed: {test_count}/{len(TEST_PROMPTS)}")
        print(f"Total tokens: ~{total_tokens}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average tokens/second: {avg_tps:.2f}")
        print("=" * 70)

        return avg_tps
    else:
        print("\nNo successful tests completed")
        return 0

def main():
    print("=" * 70)
    print("RKLLM Performance Measurement")
    print("=" * 70)
    print()
    print(f"Model: {MODEL_PATH}")
    print(f"Platform: {PLATFORM}")
    print()

    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found: {MODEL_PATH}")
        return 1

    # Start server
    print("Starting RKLLM Flask server...")
    server_dir = "/home/ubuntu/rk_llm_chat/rknn-llm/examples/rkllm_server_demo"

    # Build command to start server in background
    start_cmd = f"""
    source /home/ubuntu/rk_llm_chat/.venv/bin/activate && \
    cd {server_dir}/rkllm_server && \
    nohup python3 flask_server.py \
        --rkllm_model_path {MODEL_PATH} \
        --target_platform {PLATFORM} \
        > /tmp/rkllm_server.log 2>&1 &
    echo $!
    """

    try:
        result = subprocess.run(
            start_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.stdout.strip():
            server_pid = int(result.stdout.strip().split()[-1])
            print(f"Server PID: {server_pid}")
        else:
            print("Warning: Could not determine server PID")
            server_pid = None

        # Wait for server to be ready
        if not wait_for_server():
            print("Error: Server failed to start")
            if os.path.exists('/tmp/rkllm_server.log'):
                print("\nServer log:")
                with open('/tmp/rkllm_server.log', 'r') as f:
                    print(f.read())
            return 1

        # Run performance tests
        avg_tps = measure_performance()

        # Cleanup - stop server
        print()
        print("Stopping server...")
        if server_pid:
            try:
                os.kill(server_pid, signal.SIGTERM)
                time.sleep(2)
            except:
                pass

        # Also kill by process name as backup
        subprocess.run("pkill -f flask_server.py", shell=True, capture_output=True)

        print("Done!")
        print()
        print(f"RESULT: {avg_tps:.2f} tokens/second")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        subprocess.run("pkill -f flask_server.py", shell=True, capture_output=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
