#!/bin/bash
# Master deployment script - deploys everything to remote host

set -e  # Exit on error

# Remote host configuration
REMOTE_USER="ubuntu"
REMOTE_HOST="192.168.68.72"
REMOTE_PATH="/home/ubuntu/rk_llm_chat"
REMOTE_PASS="ubuntu1234"

echo "=========================================="
echo "RK LLM Chat - Full Deployment"
echo "=========================================="
echo "Remote host: $REMOTE_USER@$REMOTE_HOST"
echo "Remote path: $REMOTE_PATH"
echo ""

# Step 1: Deploy program files
echo "Step 1: Deploying program files..."
./deploy_program.sh
echo ""

# Step 2: Deploy model file
echo "Step 2: Deploying model file..."
./deploy_model.sh
echo ""

# Step 3: Initialize environment on remote
echo "Step 3: Initializing environment on remote host..."
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && bash init_env.sh"
echo ""

# Step 4: Run demo
echo "Step 4: Running demo on remote host..."
echo "Note: This will take some time to load the model and generate responses."
echo ""
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && source .venv/bin/activate && python demo.py"

echo ""
echo "=========================================="
echo "Deployment and demo completed!"
echo "=========================================="
