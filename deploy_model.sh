#!/bin/bash
# Deploy RKLLM models to remote host
# Automatically detects all .rkllm files and only deploys missing ones

set -e  # Exit on error

# Remote host configuration
REMOTE_USER="ubuntu"
REMOTE_HOST="192.168.68.72"
REMOTE_PATH="/home/ubuntu/rk_llm_chat"
REMOTE_PASS="ubuntu1234"

echo "Checking for RKLLM model files..."
echo ""

# Find all .rkllm files in current directory
LOCAL_MODELS=(*.rkllm)

# Check if any models found
if [ ${#LOCAL_MODELS[@]} -eq 0 ] || [ ! -f "${LOCAL_MODELS[0]}" ]; then
    echo "Error: No .rkllm model files found in current directory"
    exit 1
fi

echo "Found ${#LOCAL_MODELS[@]} model file(s) locally:"
for model in "${LOCAL_MODELS[@]}"; do
    size=$(du -h "$model" | cut -f1)
    echo "  - $model ($size)"
done
echo ""

# Create remote directory
echo "Creating remote directory..."
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH"

# Get list of models already on remote
echo "Checking which models are already on remote host..."
REMOTE_MODELS=$(sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && ls *.rkllm 2>/dev/null || true")

echo ""
echo "Models on remote host:"
if [ -z "$REMOTE_MODELS" ]; then
    echo "  (none)"
else
    echo "$REMOTE_MODELS" | while read -r model; do
        echo "  - $model"
    done
fi
echo ""

# Deploy missing models
DEPLOYED_COUNT=0
SKIPPED_COUNT=0

for model in "${LOCAL_MODELS[@]}"; do
    # Check if model already exists on remote
    if echo "$REMOTE_MODELS" | grep -q "^$model\$"; then
        echo "✓ Skipping $model (already on remote)"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    else
        echo "→ Deploying $model (this may take a while)..."
        sshpass -p "$REMOTE_PASS" rsync -avz --progress "$model" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"
        echo "✓ Deployed $model"
        echo ""
        DEPLOYED_COUNT=$((DEPLOYED_COUNT + 1))
    fi
done

echo ""
echo "========================================"
echo "Deployment Summary:"
echo "  Deployed: $DEPLOYED_COUNT model(s)"
echo "  Skipped:  $SKIPPED_COUNT model(s)"
echo "========================================"
