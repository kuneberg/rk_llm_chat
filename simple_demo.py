"""
Simple RKLLM Demo using ctypes to directly call the C library
This is a simplified demo to test model loading and inference
"""
import ctypes
import sys
import os
import time

# RKLLM model path
MODEL_PATH = "Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"

def main():
    print("=" * 60)
    print("RKLLM Simple Demo")
    print("=" * 60)
    print()

    # Check if model file exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found: {MODEL_PATH}")
        return 1

    print(f"Model file: {MODEL_PATH}")
    print(f"Model size: {os.path.getsize(MODEL_PATH) / (1024**3):.2f} GB")
    print()

    # Load the RKLLM runtime library
    try:
        lib_path = "/usr/lib/librkllmrt.so"
        if not os.path.exists(lib_path):
            print(f"Error: RKLLM library not found at {lib_path}")
            print("Please run install_rkllm.sh first")
            return 1

        print(f"Loading RKLLM library from: {lib_path}")
        rkllm_lib = ctypes.CDLL(lib_path)
        print("✓ RKLLM library loaded successfully")
        print()
    except Exception as e:
        print(f"Error loading RKLLM library: {e}")
        return 1

    # Note: Full RKLLM API integration requires understanding the C API structure
    # For now, we're just verifying the library can be loaded

    print("=" * 60)
    print("Library Check Complete")
    print("=" * 60)
    print()
    print("✓ RKLLM runtime library is installed and accessible")
    print("✓ Model file is present")
    print()
    print("To run the full demo server, use:")
    print("  cd rknn-llm/examples/rkllm_server_demo")
    print("  ./build_rkllm_server_flask.sh --workshop /home/ubuntu/rk_llm_chat \\")
    print(f"    --model_path /home/ubuntu/rk_llm_chat/{MODEL_PATH} \\")
    print("    --platform rk3588")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
