"""
Performance measurement demo for RKLLM model
Measures tokens per second generation speed
"""
import time
import argparse
from chat import RKLLMChat


def count_tokens(text):
    """
    Simple token counter (approximation using word count)
    For more accurate counting, use a proper tokenizer
    """
    return len(text.split())


def run_performance_test(model_path, prompts=None, max_new_tokens=512):
    """
    Run performance tests on the RKLLM model

    Args:
        model_path: Path to the RKLLM model
        prompts: List of prompts to test (default: use built-in prompts)
        max_new_tokens: Maximum tokens to generate per prompt

    Returns:
        Dictionary containing performance metrics
    """
    if prompts is None:
        prompts = [
            "What is artificial intelligence?",
            "Explain quantum computing in simple terms.",
            "Write a short story about a robot learning to paint.",
            "What are the main differences between Python and JavaScript?",
            "Describe the process of photosynthesis."
        ]

    print(f"Initializing RKLLM Chat with model: {model_path}")
    chat = RKLLMChat(model_path)

    # Measure model loading time
    load_start = time.time()
    chat.load_model()
    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.2f} seconds\n")

    results = []
    total_tokens = 0
    total_time = 0

    try:
        for i, prompt in enumerate(prompts, 1):
            print(f"Test {i}/{len(prompts)}")
            print(f"Prompt: {prompt}")
            print("Response: ", end="", flush=True)

            response = ""
            start_time = time.time()
            first_token_time = None

            # Stream tokens and measure performance
            token_count = 0
            for token in chat.chat_stream(prompt, max_new_tokens=max_new_tokens):
                if first_token_time is None:
                    first_token_time = time.time()

                print(token, end="", flush=True)
                response += token
                token_count += 1

            end_time = time.time()
            print("\n")

            # Calculate metrics
            total_gen_time = end_time - start_time
            ttft = first_token_time - start_time if first_token_time else 0
            tokens_generated = count_tokens(response)

            tokens_per_second = tokens_generated / total_gen_time if total_gen_time > 0 else 0

            result = {
                'prompt': prompt,
                'response': response,
                'tokens_generated': tokens_generated,
                'time_taken': total_gen_time,
                'ttft': ttft,  # Time to first token
                'tokens_per_second': tokens_per_second
            }
            results.append(result)

            total_tokens += tokens_generated
            total_time += total_gen_time

            print(f"Tokens generated: {tokens_generated}")
            print(f"Time taken: {total_gen_time:.2f}s")
            print(f"Time to first token: {ttft:.3f}s")
            print(f"Tokens/second: {tokens_per_second:.2f}")
            print("-" * 60 + "\n")

    finally:
        chat.release()

    # Calculate overall statistics
    avg_tokens_per_second = total_tokens / total_time if total_time > 0 else 0
    avg_ttft = sum(r['ttft'] for r in results) / len(results) if results else 0

    print("=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Model loading time: {load_time:.2f}s")
    print(f"Total prompts tested: {len(prompts)}")
    print(f"Total tokens generated: {total_tokens}")
    print(f"Total generation time: {total_time:.2f}s")
    print(f"Average tokens/second: {avg_tokens_per_second:.2f}")
    print(f"Average time to first token: {avg_ttft:.3f}s")
    print("=" * 60)

    return {
        'load_time': load_time,
        'total_tokens': total_tokens,
        'total_time': total_time,
        'avg_tokens_per_second': avg_tokens_per_second,
        'avg_ttft': avg_ttft,
        'results': results
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RKLLM Performance Demo')
    parser.add_argument(
        '--model',
        type=str,
        default='Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm',
        help='Path to the RKLLM model file'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=512,
        help='Maximum number of tokens to generate per prompt'
    )
    parser.add_argument(
        '--prompt',
        type=str,
        action='append',
        help='Custom prompt to test (can be specified multiple times)'
    )

    args = parser.parse_args()

    # Use custom prompts if provided
    prompts = args.prompt if args.prompt else None

    run_performance_test(
        model_path=args.model,
        prompts=prompts,
        max_new_tokens=args.max_tokens
    )
