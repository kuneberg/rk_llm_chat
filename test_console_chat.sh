#!/bin/bash
# Test console chat functionality

echo "Testing console chat..."
echo ""

# Send a test message using Python
python3 << 'EOF'
import requests
import sys

try:
    response = requests.post(
        'http://127.0.0.1:8080/rkllm_chat',
        json={"messages": [{"role": "user", "content": "Hi, say hello!"}], "stream": False},
        timeout=60
    )

    if response.status_code == 200:
        result = response.json()
        text = result['choices'][0]['message']['content']
        print("✓ Console chat is working!")
        print()
        print("Test response:")
        print(text[:200] + "..." if len(text) > 200 else text)
        sys.exit(0)
    else:
        print(f"✗ Error: HTTP {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
EOF
