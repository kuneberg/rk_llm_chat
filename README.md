# RK LLM Chat Demo

A demo application for running and benchmarking Rockchip RKLLM models on RK3588 hardware.

**Status:** ✅ **DEPLOYED AND VERIFIED** - All components installed and tested on remote hardware.

**Performance:** 4.75 tokens/second average on RK3588

## Quick Start - Console Chat

To start an interactive chat session on the RK3588 device:

1. **SSH into the device:**
   ```bash
   ssh ubuntu@192.168.68.72
   # Password: ubuntu1234
   ```

2. **Start the RKLLM server:**
   ```bash
   cd /home/ubuntu/rk_llm_chat
   bash start_chat_server.sh
   ```
   This will initialize the model (takes ~15-20 seconds).

3. **Start the console chat:**
   ```bash
   bash start_console_chat.sh
   ```

4. **Chat with the AI:**
   ```
   You: What is artificial intelligence?
   Assistant: [Model's response will appear here]
   ```

5. **Exit chat:** Type `quit`, `exit`, or press `Ctrl+C`

6. **Stop the server when done:**
   ```bash
   bash stop_chat_server.sh
   ```

**Note:** The server runs in the background and can serve multiple chat sessions. You only need to start it once.

## Project Structure

### Console Chat (Recommended)
- `console_chat.py` - **Interactive console chat** with the RKLLM model
- `start_chat_server.sh` - Start the RKLLM server in background
- `start_console_chat.sh` - Start the console chat interface
- `stop_chat_server.sh` - Stop the background server

### Core Files
- `simple_demo.py` - Verifies RKLLM library and model
- `chat.py` - Alternative chat interface (requires ctypes integration)
- `demo.py` - Performance measurement script
- `run_demo.sh` - Demo runner

### Setup & Deployment
- `init_env.sh` - Initialize Python virtual environment
- `install_rkllm.sh` - Install RKLLM toolkit on RK3588
- `deploy_model.sh` - Deploy model file to remote host
- `deploy_program.sh` - Deploy program files to remote host
- `deploy_all.sh` - Master deployment script

### Documentation
- `requirements.txt` - Python dependencies
- `README.md` - This file
- `DEPLOYMENT_STATUS.md` - **Complete deployment status and verification**
- `INSTALL_RKLLM.md` - RKLLM installation instructions

## Local Setup

1. Initialize the environment:
```bash
./init_env.sh
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Run the performance demo:
```bash
python demo.py
```

4. Or run interactive chat:
```bash
python chat.py
```

## Remote Deployment

The project includes scripts to deploy and run on a remote Rockchip device.

### Remote Host Configuration
- Host: ubuntu@192.168.68.72
- Password: ubuntu1234
- Deploy path: /home/ubuntu/rk_llm_chat

### Deployment Options

**Option 1: Full deployment (recommended)**
```bash
./deploy_all.sh
```
This will:
1. Deploy program files
2. Deploy model file
3. Initialize environment on remote
4. Run the demo

**Option 2: Selective deployment**

Deploy only program files:
```bash
./deploy_program.sh
```

Deploy only model file:
```bash
./deploy_model.sh
```

## Requirements

- Python 3.x
- `sshpass` (for automated remote deployment)
  - macOS: `brew install sshpass`
  - Ubuntu: `sudo apt-get install sshpass`
- **RKLLM toolkit** - Required to run the model
  - Not available on PyPI, must be installed separately
  - See INSTALL_RKLLM.md for installation instructions
  - Required on the Rockchip hardware to run inference

## Model

The project uses the Qwen3-4B model optimized for RK3588:
- **File:** `Qwen3-4B-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm`
- **Size:** 4.51 GB
- **Toolkit:** RKLLM v1.2.1
- **Quantization:** W8A8 (8-bit weights and activations)

## Performance Metrics

**Verified Performance:** 4.75 tokens/second (average)

Detailed benchmark results:
- Test 1 ("What is AI?"): 5.15 tokens/s
- Test 2 ("Explain deep learning"): 4.58 tokens/s
- Test 3 ("What are neural networks?"): 4.67 tokens/s

See `PERFORMANCE_RESULTS.md` for detailed analysis.
