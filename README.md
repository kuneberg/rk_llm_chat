# RK LLM Chat Demo

A demo application for running and benchmarking Rockchip RKLLM models on RK3588 hardware.

**Performance:** 4.75 tokens/second average on RK3588
**Status:** ✅ Deployed and verified on remote hardware

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
  - [Standalone Console Chat](#standalone-console-chat)
  - [Benchmark All Models](#benchmark-all-models)
  - [Server-Based Architecture](#server-based-architecture)
- [Deployment](#deployment)
- [Model Information](#model-information)
- [Performance Metrics](#performance-metrics)

## Prerequisites

### On Local Machine (for deployment)
- Python 3.x
- `sshpass` for automated SSH deployment
  - macOS: `brew install sshpass`
  - Ubuntu: `sudo apt-get install sshpass`

### On RK3588 Device
- Ubuntu/Linux OS
- Python 3.x with venv support
- RKLLM runtime library (librkllmrt.so)

## Setup

Follow these steps to set up the environment on your RK3588 device:

### 1. Initialize Python Environment

First, create and activate the Python virtual environment:

```bash
cd /home/ubuntu/rk_llm_chat
./init_env.sh
```

This will:
- Create a `.venv` directory
- Install required Python packages from `requirements.txt`
- Set up the development environment

### 2. Install RKLLM Runtime

Install the RKLLM runtime library on your RK3588 device:

```bash
./install_rkllm.sh
```

This will:
- Download RKLLM runtime v1.2.1b1
- Install `librkllmrt.so` to `/usr/lib/`
- Verify the installation

**Important:** This step is required only once per device. The RKLLM runtime enables NPU acceleration for model inference.

## Usage

### Standalone Console Chat

The standalone console chat runs the model directly within the application (no separate server needed).

**Features:**
- Interactive chat interface
- Automatic model selection from available .rkllm files
- Real-time token generation
- Performance metrics (tokens/s) after each response

**To run:**

```bash
./run_standalone_chat.sh
```

**Usage:**
```
Available RKLLM models:
  1. Qwen3-4B-opt-0.rkllm (4.51 GB)
  2. Qwen3-4B-opt-1.rkllm (4.51 GB)

Select model (1-2): 1

Loading model...
✓ Model loaded successfully!

You: What is artificial intelligence?
Assistant: [Response appears here with streaming output]

[Tokens: 150 | Speed: 4.75 tokens/s | Time: 31.6s]

You: quit
```

**Commands:**
- Type your message and press Enter
- Type `quit`, `exit`, or `q` to exit
- Press `Ctrl+C` to interrupt

### Benchmark All Models

Run comprehensive benchmarks on all .rkllm models in the directory:

```bash
./benchmark.sh
```

This will:
- Automatically detect all .rkllm model files
- Test each model with the prompt "What is LLM"
- Measure load time, tokens generated, inference time, and tokens/s
- Display results in a formatted table
- Generate `benchmark_report.md` with detailed results

**Example output:**
```
====================================================================================================
BENCHMARK RESULTS
====================================================================================================

Model                                              Size (GB)    Load (s)   Tokens   Time (s)   Speed (tok/s)
----------------------------------------------------------------------------------------------------
Qwen3-4B-opt-0.rkllm                              4.51         18.2       145      30.52      4.75
Qwen3-4B-opt-1.rkllm                              4.51         17.8       148      29.87      4.96
====================================================================================================
```

### Server-Based Architecture

For applications that need to keep the model loaded in memory, use the server-based approach:

#### Start the Server

```bash
./start_chat_server.sh
```

This will:
- Load the model into memory (~15-20 seconds)
- Start a Flask HTTP server in the background
- Save the server PID for later shutdown

**Note:** The server runs in the background and can serve multiple clients simultaneously.

#### Run Console Chat Client

Once the server is running, start the console chat client:

```bash
./start_console_chat.sh
```

This provides an interactive chat interface that connects to the server via HTTP API.

#### Run Performance Demo

To test the server and measure performance:

```bash
./run_perf_test.sh
```

This will run multiple test prompts and display performance metrics.

#### Stop the Server

When done, stop the background server:

```bash
./stop_chat_server.sh
```

## Deployment

The project includes automated deployment scripts for remote RK3588 devices.

### Remote Host Configuration
- **Host:** ubuntu@192.168.68.72
- **Password:** ubuntu1234
- **Path:** /home/ubuntu/rk_llm_chat

### Deploy Everything

Full deployment (recommended for first-time setup):

```bash
./deploy_all.sh
```

This will:
1. Deploy all program files
2. Deploy all .rkllm model files (only missing ones)
3. Initialize the Python environment on remote
4. Verify the installation

### Selective Deployment

**Deploy only program files:**
```bash
./deploy_program.sh
```
Use this when you've updated scripts but not models.

**Deploy only model files:**
```bash
./deploy_model.sh
```
The script automatically:
- Detects all .rkllm files locally
- Checks which models are already on the remote
- Only uploads missing models
- Shows deployment summary

## Model Information

### Supported Models

The project works with any RKLLM-converted model. Example models:

- **Qwen3-4B-opt-0** (base optimization)
  - File: `Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm`
  - Size: 4.51 GB
  - Performance: ~4.75 tokens/s

- **Qwen3-4B-opt-1** (enhanced optimization)
  - File: `Qwen3-4B-rk3588-w8a8-opt-1-hybrid-ratio-0.0.rkllm`
  - Size: 4.51 GB
  - Performance: ~4.96 tokens/s

### Model Format

- **Platform:** RK3588
- **Toolkit:** RKLLM v1.2.1
- **Quantization:** W8A8 (8-bit weights and activations)
- **Runtime:** RKLLM v1.2.1b1
- **NPU:** 3 cores enabled for inference

## Performance Metrics

### Verified Performance

**Average:** 4.75 tokens/second on RK3588

### Detailed Benchmarks

| Test | Prompt | Tokens/s |
|------|--------|----------|
| 1 | "What is AI?" | 5.15 |
| 2 | "Explain deep learning" | 4.58 |
| 3 | "What are neural networks?" | 4.67 |

### Hardware Configuration

- **Platform:** RK3588 (ARM64)
- **NPU:** 3 cores @ 1GHz
- **CPU:** 4 cores enabled (cores 4-7)
- **Memory:** Model loaded to NPU memory
- **Driver:** NPU driver v0.9.7

## Project Structure

```
rk_llm_chat/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
│
├── Standalone Console
│   ├── standalone_console.py   # Standalone chat with model selection
│   └── run_standalone_chat.sh  # Runner script
│
├── Benchmark
│   ├── benchmark.py            # Multi-model benchmark tool
│   └── benchmark.sh            # Benchmark runner
│
├── Server-Based Architecture
│   ├── console_chat.py         # Console chat client
│   ├── start_chat_server.sh   # Start background server
│   ├── stop_chat_server.sh    # Stop background server
│   └── start_console_chat.sh  # Start console client
│
├── Setup Scripts
│   ├── init_env.sh            # Initialize Python environment
│   └── install_rkllm.sh       # Install RKLLM runtime
│
├── Deployment Scripts
│   ├── deploy_all.sh          # Deploy everything
│   ├── deploy_program.sh      # Deploy program files only
│   └── deploy_model.sh        # Deploy model files only
│
└── Legacy/Development
    ├── chat.py                # Alternative chat implementation
    ├── demo.py                # Performance demo
    ├── simple_demo.py         # Library verification
    ├── performance_demo.py    # Advanced performance testing
    └── measure_performance.py # Server performance measurement
```

## Troubleshooting

### Model not found
Make sure .rkllm model files are in the same directory as the scripts.

### RKLLM library not found
Run `./install_rkllm.sh` to install the RKLLM runtime library.

### Server won't start
Check if a server is already running: `ps aux | grep flask_server`

### Permission denied
Make scripts executable: `chmod +x *.sh *.py`

### Version mismatch
Ensure the model was converted with the same RKLLM toolkit version as the runtime.

## Documentation

- `DEPLOYMENT_STATUS.md` - Detailed deployment verification
- `PERFORMANCE_RESULTS.md` - Comprehensive performance analysis
- `INSTALL_RKLLM.md` - RKLLM installation guide

## License

This is a demo project for Rockchip RKLLM on RK3588 hardware.
