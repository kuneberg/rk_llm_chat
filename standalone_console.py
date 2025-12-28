#!/usr/bin/env python3
"""
RKLLM Standalone Console Chat
Standalone interactive chat with RKLLM model - no separate server needed
Model is loaded and run directly within this script
"""

import ctypes
import sys
import os
import time
import glob

# Library configuration
LIB_PATH = "/usr/lib/librkllmrt.so"

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
        print("\n[Error during generation]", file=sys.stderr)
    elif state == LLMCallState.RKLLM_RUN_NORMAL:
        global_state = state
        text = result.contents.text.decode('utf-8', errors='ignore')
        global_text.append(text)
        global_token_count += 1
        print(text, end='', flush=True)

# Create callback type
callback_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(RKLLMResult), ctypes.c_void_p, ctypes.c_int)
callback = callback_type(callback_impl)

def select_model_file():
    """List available .rkllm model files and let user select one"""
    # Find all .rkllm files in current directory
    model_files = glob.glob("*.rkllm")

    if not model_files:
        print("Error: No .rkllm model files found in current directory")
        print(f"Current directory: {os.getcwd()}")
        return None

    if len(model_files) == 1:
        # Only one model found, use it automatically
        print(f"Found model: {model_files[0]}")
        return model_files[0]

    # Multiple models found, let user choose
    print("Available RKLLM models:")
    print()
    for i, model in enumerate(model_files, 1):
        file_size = os.path.getsize(model) / (1024**3)  # Size in GB
        print(f"  {i}. {model} ({file_size:.2f} GB)")
    print()

    while True:
        try:
            choice = input(f"Select model (1-{len(model_files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(model_files):
                selected = model_files[idx]
                print(f"Selected: {selected}")
                print()
                return selected
            else:
                print(f"Please enter a number between 1 and {len(model_files)}")
        except ValueError:
            print("Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled")
            return None

# RKLLM Model Class
class RKLLM:
    def __init__(self, model_path):
        print(f"Loading model: {model_path}")
        print("This may take 15-20 seconds...")
        print()

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

        print("✓ Model loaded successfully!")
        print()

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
            print(f"\n[Error: Inference failed with code {ret}]", file=sys.stderr)
            return "", 0

        # Wait for completion
        while global_state != LLMCallState.RKLLM_RUN_FINISH and global_state != LLMCallState.RKLLM_RUN_ERROR:
            time.sleep(0.01)

        return ''.join(global_text), global_token_count

    def release(self):
        self.rkllm_destroy(self.handle)

def main():
    """Main chat loop"""
    print("=" * 70)
    print("RKLLM Standalone Console Chat")
    print("=" * 70)
    print()

    # Select model file
    model_path = select_model_file()
    if not model_path:
        return 1

    # Initialize model
    try:
        model = RKLLM(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return 1

    print("Type your message and press Enter to chat.")
    print("Type 'quit', 'exit', or press Ctrl+C to end the conversation.")
    print()
    print("-" * 70)
    print()

    # Chat loop
    try:
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                print("Assistant: ", end="", flush=True)
                start_time = time.time()

                response, token_count = model.run(user_input)

                elapsed = time.time() - start_time
                tokens_per_sec = token_count / elapsed if elapsed > 0 else 0
                print()
                print()
                print(f"[Tokens: {token_count} | Speed: {tokens_per_sec:.2f} tokens/s | Time: {elapsed:.1f}s]")
                print()
                print("-" * 70)
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print()

    finally:
        print("\nReleasing model...")
        model.release()
        print("Done!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
