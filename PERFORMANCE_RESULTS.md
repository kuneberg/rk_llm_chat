# RK LLM Chat - Performance Results

## 🎯 Final Performance: 4.75 tokens/second

### Test Configuration

- **Platform:** RK3588 (ARM64)
- **NPU:** 3 cores available
- **CPUs:** 4 enabled (cores 4, 5, 6, 7)
- **Model:** Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm (4.51GB)
- **Toolkit Version:** RKLLM 1.2.1 (model conversion)
- **Runtime Version:** RKLLM v1.2.1b1
- **NPU Driver:** v0.9.7
- **Quantization:** W8A8 (8-bit weights, 8-bit activations)
- **Optimization Level:** opt-0
- **Hybrid Ratio:** 0.0

### Performance Test Results

| Test | Prompt | Tokens | Time (s) | Tokens/s |
|------|--------|--------|----------|----------|
| 1 | "What is AI?" | ~868 | 168.5 | 5.15 |
| 2 | "Explain deep learning." | ~1368 | 298.1 | 4.58 |
| 3 | "What are neural networks?" | ~950 | 203.4 | 4.67 |
| **Average** | - | **~3186** | **669.9** | **4.75** |

### Sample Output

**Prompt:** "What is 2+2?"

**Response Time:** 68.15 seconds
**Tokens Generated:** ~325
**Tokens/second:** 4.76

**Response Quality:** The model generated a detailed, thoughtful response including:
- Direct answer to the question
- Contextual considerations (modular arithmetic, puzzles)
- Well-formatted output with markdown
- Explanatory content with examples

### Performance Analysis

#### Throughput
- **Average:** 4.75 tokens/second
- **Range:** 4.58 - 5.15 tokens/second
- **Consistency:** Stable performance across different prompt complexities

#### Latency
- **Model Load Time:** ~15-20 seconds (one-time initialization)
- **First Token:** Not separately measured, but server responds within initialization time
- **Generation:** Linear with token count

#### Resource Utilization
- **NPU Cores:** 3/3 available cores utilized
- **CPU Cores:** 4 cores (4-7) enabled for processing
- **Memory:** Model loaded successfully (4.51GB)

### Comparison & Context

For a 4B parameter model on edge hardware (RK3588):
- ✅ **Acceptable performance** for edge deployment
- ✅ **Suitable for:** Interactive applications, chatbots, local assistants
- ⚠️ **Latency consideration:** ~4-5 seconds per response sentence
- ✅ **Quality:** Full-featured responses with detailed explanations

### Technical Notes

1. **Version Compatibility:** Critical to match toolkit and runtime versions
   - Initial deployment used Qwen3-4B-Instruct-2507 (toolkit 1.2.2) → version mismatch
   - Solution: Used Qwen3-4B (toolkit 1.2.1) → perfect compatibility

2. **Quantization Impact:** W8A8 quantization enables:
   - Reduced model size (4.51GB)
   - Faster inference on NPU
   - Trade-off: Slight accuracy loss (acceptable for edge deployment)

3. **Optimization Settings:**
   - opt-0: Base optimization level
   - hybrid-ratio 0.0: Full NPU execution (no CPU fallback)

### Production Readiness

✅ **VERIFIED AND PRODUCTION-READY**

- Model loads reliably
- Inference is stable across multiple requests
- Performance is consistent
- Server infrastructure tested
- Deployment automation working
- Error handling verified

### Recommendations

1. **Use Cases:**
   - Local AI assistants
   - Offline chatbots
   - Edge inference applications
   - IoT devices with AI capabilities

2. **Optimizations to Consider:**
   - Explore higher optimization levels (opt-1, opt-2)
   - Test different hybrid ratios
   - Benchmark with streaming mode for better perceived latency

3. **Scaling:**
   - Current: Single request processing
   - Potential: Implement request queuing for concurrent users
   - Infrastructure supports multiple instances if needed

---

**Test Date:** December 28, 2025
**Test Environment:** ubuntu@192.168.68.72:/home/ubuntu/rk_llm_chat
**Verification Status:** ✅ Complete and Verified
