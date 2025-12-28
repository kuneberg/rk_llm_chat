"""
Chat interface for Rockchip RKLLM model
"""
import os
from rkllm.api import RKLLM


class RKLLMChat:
    def __init__(self, model_path):
        """
        Initialize the RKLLM chat interface

        Args:
            model_path: Path to the RKLLM model file
        """
        self.model_path = model_path
        self.rkllm = None

    def load_model(self):
        """Load the RKLLM model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        print(f"Loading model from {self.model_path}...")
        self.rkllm = RKLLM()

        # Load model
        ret = self.rkllm.load_rkllm(self.model_path)
        if ret != 0:
            raise RuntimeError(f"Failed to load model, error code: {ret}")

        print("Model loaded successfully!")

    def chat(self, prompt, max_new_tokens=512, temperature=0.7, top_p=0.9):
        """
        Generate a response to the given prompt

        Args:
            prompt: Input prompt/question
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter

        Returns:
            Generated response text
        """
        if self.rkllm is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Run inference
        result = self.rkllm.run(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p
        )

        return result

    def chat_stream(self, prompt, max_new_tokens=512, temperature=0.7, top_p=0.9):
        """
        Generate a streaming response to the given prompt

        Args:
            prompt: Input prompt/question
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter

        Yields:
            Generated tokens as they are produced
        """
        if self.rkllm is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Run streaming inference
        for token in self.rkllm.run_stream(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p
        ):
            yield token

    def release(self):
        """Release the model resources"""
        if self.rkllm is not None:
            self.rkllm.release()
            self.rkllm = None
            print("Model released")


if __name__ == "__main__":
    # Interactive chat demo
    model_path = "Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm"

    chat = RKLLMChat(model_path)
    chat.load_model()

    print("\nRKLLM Chat Interface")
    print("Type 'quit' or 'exit' to end the conversation\n")

    try:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("Assistant: ", end="", flush=True)

            # Use streaming for interactive experience
            response = ""
            for token in chat.chat_stream(user_input):
                print(token, end="", flush=True)
                response += token

            print()  # New line after response

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        chat.release()
