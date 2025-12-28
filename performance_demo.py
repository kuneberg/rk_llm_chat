#!/usr/bin/env python3
"""
RKLLM Performance Demo
Measures tokens/second generation performance using direct C library calls
Based on the official rkllm_server flask_server.py implementation
"""

import ctypes
import sys
import os
import time
from enum import IntEnum

# Model configuration
MODEL_PATH = "Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"
LIB_PATH = "/usr/lib/librkllmrt.so"

# Enums from RKLLM C API
class RKLLMInferMode(IntEnum):
    RKLLM_INFER_GENERATE = 0
    RKLLM_INFER_GET_LAST_HIDDEN_LAYER = 1
    RKLLM_INFER_GET_LOGITS = 2

class LLMCallState(IntEnum):
    RKLLM_RUN_NORMAL = 0
    RKLLM_RUN_WAITING = 1
    RKLLM_RUN_FINISH = 2
    RKLLM_RUN_ERROR = 3

# C Structures
class RKLLMExtendParam(ctypes.Structure):
    _fields_ = [
        ("base_domain_id", ctypes.c_int),
        ("reserved", ctypes.c_byte * 112)
    ]

class RKLLMParam(ctypes.Structure):
    _fields_ = [
        ("model_path", ctypes.c_char_p),
        ("max_context_len", ctypes.c_int),
        ("max_new_tokens", ctypes.c_int),
        ("top_k", ctypes.c_int),
        ("top_p", ctypes.c_float),
        ("temperature", ctypes.c_float),
        ("repeat_penalty", ctypes.c_float),
        ("frequency_penalty", ctypes.c_float),
        ("presence_penalty", ctypes.c_float),
        ("mirostat", ctypes.c_int),
        ("mirostat_tau", ctypes.c_float),
        ("mirostat_eta", ctypes.c_float),
        ("skip_special_token", ctypes.c_bool),
        ("is_async", ctypes.c_bool),
        ("img_start", ctypes.c_char_p),
        ("img_end", ctypes.c_char_p),
        ("img_content", ctypes.c_char_p),
        ("extend_param", RKLLMExtendParam)
    ]

class RKLLMInput(ctypes.Structure):
    _fields_ = [
        ("prompt", ctypes.c_char_p),
        ("prompt_len", ctypes.c_int)
    ]

class RKLLMResult(ctypes.Structure):
    _fields_ = [
        ("text", ctypes.c_char_p),
        ("size", ctypes.c_int)
    ]

# Global variables for callback
global_text = ""
global_state = -1
token_count = 0
first_token_time = None

# Callback function
def callback_impl(result, userdata, state):
    global global_text, global_state, token_count, first_token_time

    if first_token_time is None and state == LLMCallState.RKLLM_RUN_NORMAL:
        first_token_time = time.time()

    if state == LLMCallState.RKLLM_RUN_FINISH:
        global_state = state
    elif state == LLMCallState.RKLLM_RUN_ERROR:
        global_state = state
        print("Error during generation", file=sys.stderr)
    elif state == LLMCallState.RKLLM_RUN_NORMAL:
        global_state = state
        text = result.contents.text.decode('utf-8', errors='ignore')
        global_text += text
        token_count += 1

# Performance test function
def run_performance_test():
    global global_text, global_state, token_count, first_token_time

    print("=" * 70)
    print("RKLLM Performance Test")
    print("=" * 70)
    print()

    # Check files
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found: {MODEL_PATH}")
        return 1

    if not os.path.exists(LIB_PATH):
        print(f"Error: RKLLM library not found: {LIB_PATH}")
        return 1

    print(f"Model: {MODEL_PATH}")
    print(f"Size: {os.path.getsize(MODEL_PATH) / (1024**3):.2f} GB")
    print()

    # Load library
    print("Loading RKLLM library...")
    try:
        rkllm_lib = ctypes.CDLL(LIB_PATH)
    except Exception as e:
        print(f"Error loading library: {e}")
        return 1

    print("✓ Library loaded")
    print()

    # Setup callback
    callback_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(RKLLMResult), ctypes.c_void_p, ctypes.c_int)
    callback = callback_type(callback_impl)

    # Initialize model
    print("Initializing model (this may take a while)...")
    init_start = time.time()

    handle = ctypes.c_void_p()
    param = RKLLMParam()
    param.model_path = MODEL_PATH.encode('utf-8')
    param.max_context_len = 512
    param.max_new_tokens = 256
    param.skip_special_token = True
    param.top_k = 1
    param.top_p = 0.9
    param.temperature = 0.8
    param.repeat_penalty = 1.1
    param.frequency_penalty = 0.0
    param.presence_penalty = 0.0
    param.is_async = False

    ret = rkllm_lib.rkllm_init(ctypes.byref(handle), param, callback)

    init_time = time.time() - init_start

    if ret != 0:
        print(f"✗ Failed to initialize model (error code: {ret})")
        return 1

    print(f"✓ Model initialized in {init_time:.2f}s")
    print()

    # Test prompts
    prompts = [
        "What is artificial intelligence?",
        "Explain quantum computing in simple terms.",
        "Write a short poem about coding.",
    ]

    total_tokens = 0
    total_time = 0

    print("=" * 70)
    print("Running Performance Tests")
    print("=" * 70)
    print()

    for i, prompt in enumerate(prompts, 1):
        global_text = ""
        global_state = -1
        token_count = 0
        first_token_time = None

        print(f"Test {i}/{len(prompts)}")
        print(f"Prompt: {prompt}")
        print()

        # Create input
        rkllm_input = RKLLMInput()
        rkllm_input.prompt = prompt.encode('utf-8')

        # Run inference
        start_time = time.time()
        ret = rkllm_lib.rkllm_run(handle, rkllm_input, None, None)
        end_time = time.time()

        if ret != 0:
            print(f"✗ Inference failed (error code: {ret})")
            continue

        # Calculate metrics
        elapsed = end_time - start_time
        ttft = (first_token_time - start_time) if first_token_time else 0

        # Estimate tokens (rough approximation)
        estimated_tokens = len(global_text.split()) * 1.3
        tps = estimated_tokens / elapsed if elapsed > 0 else 0

        print(f"Response: {global_text[:150]}...")
        print()
        print(f"Time: {elapsed:.2f}s")
        print(f"Time to first token: {ttft:.3f}s")
        print(f"Estimated tokens: ~{int(estimated_tokens)}")
        print(f"Tokens/second: {tps:.2f}")
        print("-" * 70)
        print()

        total_tokens += estimated_tokens
        total_time += elapsed

    # Summary
    avg_tps = total_tokens / total_time if total_time > 0 else 0

    print("=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"Model load time: {init_time:.2f}s")
    print(f"Total prompts: {len(prompts)}")
    print(f"Total tokens: ~{int(total_tokens)}")
    print(f"Total inference time: {total_time:.2f}s")
    print(f"Average tokens/second: {avg_tps:.2f}")
    print("=" * 70)

    # Cleanup
    print()
    print("Releasing model...")
    rkllm_lib.rkllm_destroy(handle)
    print("✓ Done")

    return 0

if __name__ == "__main__":
    sys.exit(run_performance_test())
