#!/usr/bin/env python3
"""
RKLLM Console Chat
Interactive chat interface for RKLLM models using the Flask server API
"""

import requests
import sys
import time
import json

# Server configuration
SERVER_URL = 'http://127.0.0.1:8080/rkllm_chat'

def chat_loop():
    """Main chat loop"""
    print("=" * 70)
    print("RKLLM Console Chat")
    print("=" * 70)
    print()
    print("Type your message and press Enter to chat.")
    print("Type 'quit', 'exit', or press Ctrl+C to end the conversation.")
    print()
    print("-" * 70)
    print()

    session = requests.Session()
    session.keep_alive = False

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            # Send request to server
            try:
                print("Assistant: ", end="", flush=True)
                start_time = time.time()

                response = session.post(
                    SERVER_URL,
                    json={
                        "messages": [{"role": "user", "content": user_input}],
                        "stream": False
                    },
                    timeout=300
                )

                elapsed = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()

                    # Extract response text
                    if 'choices' in result and len(result['choices']) > 0:
                        text = result['choices'][0]['message']['content']
                        print(text)
                    else:
                        print("(No response)")

                    # Show timing
                    print()
                    print(f"[Response time: {elapsed:.1f}s]")
                else:
                    print(f"\nError: Server returned HTTP {response.status_code}")
                    print(f"Response: {response.text[:200]}")

            except requests.exceptions.Timeout:
                print("\nError: Request timed out. The model might be processing a long response.")
            except requests.exceptions.ConnectionError:
                print("\nError: Cannot connect to server. Is the RKLLM server running?")
                print("Start the server first with: bash start_chat_server.sh")
                break
            except Exception as e:
                print(f"\nError: {e}")

            print()
            print("-" * 70)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break

if __name__ == "__main__":
    try:
        chat_loop()
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
