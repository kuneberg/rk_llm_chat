#!/usr/bin/env python3
"""
RKLLM Model Benchmark Tool
Benchmarks all .rkllm models in the current directory with a standard prompt
"""

import ctypes
import sys
import os
import time
import glob
from datetime import datetime

# Library configuration
LIB_PATH = "/usr/lib/librkllmrt.so"
BENCHMARK_PROMPT = "What is LLM"

# Load RKLLM library
rkllm_lib = ctypes.CDLL(LIB_PATH)

# Define types and structures
RKLLM_Handle_t = ctypes.c_void_p
userdata = ctypes.c_void_p(None)

# LLM Call States
class LLMCallState:
    RKLLM_RUN_NORMAL = 0
    RKLLM_RUN_WAITING = 1
    RKLLM_RUN_FINISH = 2
    RKLLM_RUN_ERROR = 3

# Input modes
class RKLLMInputMode:
    RKLLM_INPUT_PROMPT = 0
    RKLLM_INPUT_TOKEN = 1
    RKLLM_INPUT_EMBED = 2
    RKLLM_INPUT_MULTIMODAL = 3

# Infer modes
class RKLLMInferMode:
    RKLLM_INFER_GENERATE = 0
    RKLLM_INFER_GET_LAST_HIDDEN_LAYER = 1
    RKLLM_INFER_GET_LOGITS = 2

# Structure definitions
class RKLLMExtendParam(ctypes.Structure):
    _fields_ = [
        ("base_domain_id", ctypes.c_int32),
        ("embed_flash", ctypes.c_int8),
        ("enabled_cpus_num", ctypes.c_int8),
        ("enabled_cpus_mask", ctypes.c_uint32),
        ("reserved", ctypes.c_uint8 * 106)
    ]

class RKLLMParam(ctypes.Structure):
    _fields_ = [
        ("model_path", ctypes.c_char_p),
        ("max_context_len", ctypes.c_int32),
        ("max_new_tokens", ctypes.c_int32),
        ("top_k", ctypes.c_int32),
        ("n_keep", ctypes.c_int32),
        ("top_p", ctypes.c_float),
        ("temperature", ctypes.c_float),
        ("repeat_penalty", ctypes.c_float),
        ("frequency_penalty", ctypes.c_float),
        ("presence_penalty", ctypes.c_float),
        ("mirostat", ctypes.c_int32),
        ("mirostat_tau", ctypes.c_float),
        ("mirostat_eta", ctypes.c_float),
        ("skip_special_token", ctypes.c_bool),
        ("is_async", ctypes.c_bool),
        ("img_start", ctypes.c_char_p),
        ("img_end", ctypes.c_char_p),
        ("img_content", ctypes.c_char_p),
        ("extend_param", RKLLMExtendParam),
    ]

class RKLLMEmbedInput(ctypes.Structure):
    _fields_ = [
        ("embed", ctypes.POINTER(ctypes.c_float)),
        ("n_tokens", ctypes.c_size_t)
    ]

class RKLLMTokenInput(ctypes.Structure):
    _fields_ = [
        ("input_ids", ctypes.POINTER(ctypes.c_int32)),
        ("n_tokens", ctypes.c_size_t)
    ]

class RKLLMMultiModelInput(ctypes.Structure):
    _fields_ = [
        ("prompt", ctypes.c_char_p),
        ("image_embed", ctypes.POINTER(ctypes.c_float)),
        ("n_image_tokens", ctypes.c_size_t),
        ("n_image", ctypes.c_size_t),
        ("image_width", ctypes.c_size_t),
        ("image_height", ctypes.c_size_t)
    ]

class RKLLMInputUnion(ctypes.Union):
    _fields_ = [
        ("prompt_input", ctypes.c_char_p),
        ("embed_input", RKLLMEmbedInput),
        ("token_input", RKLLMTokenInput),
        ("multimodal_input", RKLLMMultiModelInput)
    ]

class RKLLMInput(ctypes.Structure):
    _fields_ = [
        ("input_mode", ctypes.c_int),
        ("input_data", RKLLMInputUnion)
    ]

class RKLLMLoraParam(ctypes.Structure):
    _fields_ = [
        ("lora_adapter_name", ctypes.c_char_p)
    ]

class RKLLMPromptCacheParam(ctypes.Structure):
    _fields_ = [
        ("save_prompt_cache", ctypes.c_int),
        ("prompt_cache_path", ctypes.c_char_p)
    ]

class RKLLMInferParam(ctypes.Structure):
    _fields_ = [
        ("mode", ctypes.c_int),
        ("lora_params", ctypes.POINTER(RKLLMLoraParam)),
        ("prompt_cache_params", ctypes.POINTER(RKLLMPromptCacheParam)),
        ("keep_history", ctypes.c_int)
    ]

class RKLLMResultLastHiddenLayer(ctypes.Structure):
    _fields_ = [
        ("hidden_states", ctypes.POINTER(ctypes.c_float)),
        ("embd_size", ctypes.c_int),
        ("num_tokens", ctypes.c_int)
    ]

class RKLLMResultLogits(ctypes.Structure):
    _fields_ = [
        ("logits", ctypes.POINTER(ctypes.c_float)),
        ("vocab_size", ctypes.c_int),
        ("num_tokens", ctypes.c_int)
    ]

class RKLLMResult(ctypes.Structure):
    _fields_ = [
        ("text", ctypes.c_char_p),
        ("token_id", ctypes.c_int),
        ("last_hidden_layer", RKLLMResultLastHiddenLayer),
        ("logits", RKLLMResultLogits)
    ]

# Global variables for callback
global_text = []
global_state = -1
global_token_count = 0

# Callback function
def callback_impl(result, userdata, state):
    global global_text, global_state, global_token_count

    if state == LLMCallState.RKLLM_RUN_FINISH:
        global_state = state
    elif state == LLMCallState.RKLLM_RUN_ERROR:
        global_state = state
    elif state == LLMCallState.RKLLM_RUN_NORMAL:
        global_state = state
        text = result.contents.text.decode('utf-8', errors='ignore')
        global_text.append(text)
        global_token_count += 1

# Create callback type
callback_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(RKLLMResult), ctypes.c_void_p, ctypes.c_int)
callback = callback_type(callback_impl)

# RKLLM Model Class
class RKLLM:
    def __init__(self, model_path):
        rkllm_param = RKLLMParam()
        rkllm_param.model_path = model_path.encode('utf-8')
        rkllm_param.max_context_len = 4096
        rkllm_param.max_new_tokens = -1
        rkllm_param.skip_special_token = True
        rkllm_param.n_keep = -1
        rkllm_param.top_k = 1
        rkllm_param.top_p = 0.9
        rkllm_param.temperature = 0.8
        rkllm_param.repeat_penalty = 1.1
        rkllm_param.frequency_penalty = 0.0
        rkllm_param.presence_penalty = 0.0
        rkllm_param.mirostat = 0
        rkllm_param.mirostat_tau = 5.0
        rkllm_param.mirostat_eta = 0.1
        rkllm_param.is_async = False
        rkllm_param.img_start = b""
        rkllm_param.img_end = b""
        rkllm_param.img_content = b""
        rkllm_param.extend_param.base_domain_id = 0
        rkllm_param.extend_param.enabled_cpus_num = 4
        rkllm_param.extend_param.enabled_cpus_mask = (1 << 4)|(1 << 5)|(1 << 6)|(1 << 7)

        self.handle = RKLLM_Handle_t()

        # Initialize
        rkllm_init = rkllm_lib.rkllm_init
        rkllm_init.argtypes = [ctypes.POINTER(RKLLM_Handle_t), ctypes.POINTER(RKLLMParam), callback_type]
        rkllm_init.restype = ctypes.c_int
        ret = rkllm_init(ctypes.byref(self.handle), ctypes.byref(rkllm_param), callback)

        if ret != 0:
            raise RuntimeError(f"Failed to initialize RKLLM model (error code: {ret})")

        # Setup run function
        self.rkllm_run = rkllm_lib.rkllm_run
        self.rkllm_run.argtypes = [RKLLM_Handle_t, ctypes.POINTER(RKLLMInput), ctypes.POINTER(RKLLMInferParam), ctypes.c_void_p]
        self.rkllm_run.restype = ctypes.c_int

        # Setup destroy function
        self.rkllm_destroy = rkllm_lib.rkllm_destroy
        self.rkllm_destroy.argtypes = [RKLLM_Handle_t]
        self.rkllm_destroy.restype = ctypes.c_int

        # Setup infer params
        self.rkllm_infer_params = RKLLMInferParam()
        ctypes.memset(ctypes.byref(self.rkllm_infer_params), 0, ctypes.sizeof(RKLLMInferParam))
        self.rkllm_infer_params.mode = RKLLMInferMode.RKLLM_INFER_GENERATE
        self.rkllm_infer_params.lora_params = None
        self.rkllm_infer_params.keep_history = 0

    def run(self, prompt):
        global global_text, global_state, global_token_count
        global_text = []
        global_state = -1
        global_token_count = 0

        rkllm_input = RKLLMInput()
        rkllm_input.input_mode = RKLLMInputMode.RKLLM_INPUT_PROMPT
        rkllm_input.input_data.prompt_input = prompt.encode('utf-8')

        ret = self.rkllm_run(self.handle, ctypes.byref(rkllm_input), ctypes.byref(self.rkllm_infer_params), None)

        if ret != 0:
            return "", 0, False

        # Wait for completion
        while global_state != LLMCallState.RKLLM_RUN_FINISH and global_state != LLMCallState.RKLLM_RUN_ERROR:
            time.sleep(0.01)

        success = global_state == LLMCallState.RKLLM_RUN_FINISH
        return ''.join(global_text), global_token_count, success

    def release(self):
        self.rkllm_destroy(self.handle)

def benchmark_model(model_path):
    """Benchmark a single model"""
    print(f"\n{'='*70}")
    print(f"Benchmarking: {model_path}")
    print(f"{'='*70}")

    # Get model file size
    file_size_gb = os.path.getsize(model_path) / (1024**3)
    print(f"Model size: {file_size_gb:.2f} GB")
    print(f"Prompt: '{BENCHMARK_PROMPT}'")
    print()

    try:
        # Load model
        print("Loading model (this may take 15-20 seconds)...")
        load_start = time.time()
        model = RKLLM(model_path)
        load_time = time.time() - load_start
        print(f"✓ Model loaded in {load_time:.1f}s")
        print()

        # Run inference
        print("Running inference...")
        inference_start = time.time()
        response, token_count, success = model.run(BENCHMARK_PROMPT)
        inference_time = time.time() - inference_start

        if not success:
            print("✗ Inference failed")
            model.release()
            return None

        tokens_per_sec = token_count / inference_time if inference_time > 0 else 0

        print(f"✓ Inference completed")
        print()
        print(f"Results:")
        print(f"  Tokens: {token_count}")
        print(f"  Time: {inference_time:.2f}s")
        print(f"  Speed: {tokens_per_sec:.2f} tokens/s")
        print()

        # Clean up
        model.release()

        return {
            'model': model_path,
            'file_size_gb': file_size_gb,
            'load_time': load_time,
            'tokens': token_count,
            'inference_time': inference_time,
            'tokens_per_sec': tokens_per_sec,
            'response': response
        }

    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def print_results_table(results):
    """Print results as a formatted table"""
    print("\n" + "="*100)
    print("BENCHMARK RESULTS")
    print("="*100)
    print()

    # Table header
    print(f"{'Model':<50} {'Size (GB)':<12} {'Load (s)':<10} {'Tokens':<8} {'Time (s)':<10} {'Speed (tok/s)':<12}")
    print("-" * 100)

    # Table rows
    for result in results:
        if result:
            print(f"{result['model']:<50} {result['file_size_gb']:<12.2f} {result['load_time']:<10.1f} "
                  f"{result['tokens']:<8} {result['inference_time']:<10.2f} {result['tokens_per_sec']:<12.2f}")

    print("="*100)
    print()

def write_markdown_report(results):
    """Write results to benchmark_report.md"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("benchmark_report.md", "w") as f:
        f.write("# RKLLM Model Benchmark Report\n\n")
        f.write(f"**Generated:** {timestamp}\n\n")
        f.write(f"**Benchmark Prompt:** \"{BENCHMARK_PROMPT}\"\n\n")
        f.write("## Results\n\n")

        # Table header
        f.write("| Model | Size (GB) | Load Time (s) | Tokens | Inference Time (s) | Speed (tokens/s) |\n")
        f.write("|-------|-----------|---------------|--------|-------------------|------------------|\n")

        # Table rows
        for result in results:
            if result:
                f.write(f"| {result['model']} | {result['file_size_gb']:.2f} | "
                       f"{result['load_time']:.1f} | {result['tokens']} | "
                       f"{result['inference_time']:.2f} | {result['tokens_per_sec']:.2f} |\n")

        f.write("\n## Detailed Responses\n\n")

        for result in results:
            if result:
                f.write(f"### {result['model']}\n\n")
                f.write(f"**Performance:**\n")
                f.write(f"- Size: {result['file_size_gb']:.2f} GB\n")
                f.write(f"- Load time: {result['load_time']:.1f}s\n")
                f.write(f"- Tokens: {result['tokens']}\n")
                f.write(f"- Inference time: {result['inference_time']:.2f}s\n")
                f.write(f"- Speed: {result['tokens_per_sec']:.2f} tokens/s\n\n")
                f.write(f"**Response:**\n```\n{result['response']}\n```\n\n")
                f.write("---\n\n")

    print(f"✓ Report written to benchmark_report.md")

def main():
    """Main benchmark function"""
    print("="*70)
    print("RKLLM MODEL BENCHMARK")
    print("="*70)
    print()

    # Find all .rkllm files
    model_files = glob.glob("*.rkllm")

    if not model_files:
        print("Error: No .rkllm model files found in current directory")
        print(f"Current directory: {os.getcwd()}")
        return 1

    print(f"Found {len(model_files)} model file(s):")
    for model in model_files:
        size = os.path.getsize(model) / (1024**3)
        print(f"  - {model} ({size:.2f} GB)")
    print()

    # Benchmark each model
    results = []
    for i, model_path in enumerate(model_files, 1):
        print(f"\n[{i}/{len(model_files)}]")
        result = benchmark_model(model_path)
        if result:
            results.append(result)

        # Small delay between models to let system cool down
        if i < len(model_files):
            print("\nWaiting 5 seconds before next model...")
            time.sleep(5)

    # Print results
    if results:
        print_results_table(results)
        write_markdown_report(results)
        print(f"\n✓ Benchmark completed: {len(results)}/{len(model_files)} models tested successfully")
    else:
        print("\n✗ No models were successfully benchmarked")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
