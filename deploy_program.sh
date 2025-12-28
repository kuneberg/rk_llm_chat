#!/bin/bash
# Deploy program files to remote host

set -e  # Exit on error

# Remote host configuration
REMOTE_USER="ubuntu"
REMOTE_HOST="192.168.68.72"
REMOTE_PATH="/home/ubuntu/rk_llm_chat"
REMOTE_PASS="ubuntu1234"

# Program files to deploy
PROGRAM_FILES=(
    "chat.py"
    "demo.py"
    "simple_demo.py"
    "performance_demo.py"
    "measure_performance.py"
    "console_chat.py"
    "standalone_console.py"
    "benchmark.py"
    "requirements.txt"
    "init_env.sh"
    "install_rkllm.sh"
    "run_demo.sh"
    "run_perf_demo.sh"
    "run_perf_test.sh"
    "start_chat_server.sh"
    "stop_chat_server.sh"
    "start_console_chat.sh"
    "run_standalone_chat.sh"
    "benchmark.sh"
)

echo "Deploying program files to $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo ""

# Create remote directory
echo "Creating remote directory..."
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH"

# Copy program files
echo "Copying program files..."
for file in "${PROGRAM_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  - $file"
        sshpass -p "$REMOTE_PASS" scp -o StrictHostKeyChecking=no "$file" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"
    else
        echo "  - Warning: $file not found, skipping"
    fi
done

# Make scripts executable on remote
echo ""
echo "Setting permissions on remote host..."
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "chmod +x $REMOTE_PATH/init_env.sh $REMOTE_PATH/install_rkllm.sh $REMOTE_PATH/run_demo.sh $REMOTE_PATH/run_perf_demo.sh $REMOTE_PATH/run_perf_test.sh $REMOTE_PATH/performance_demo.py $REMOTE_PATH/measure_performance.py $REMOTE_PATH/console_chat.py $REMOTE_PATH/standalone_console.py $REMOTE_PATH/benchmark.py $REMOTE_PATH/start_chat_server.sh $REMOTE_PATH/stop_chat_server.sh $REMOTE_PATH/start_console_chat.sh $REMOTE_PATH/run_standalone_chat.sh $REMOTE_PATH/benchmark.sh"

echo ""
echo "Program files deployed successfully!"
