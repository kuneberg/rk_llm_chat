#!/bin/bash
# Install RKLLM toolkit on Rockchip development board
# Based on: https://docs.radxa.com/en/rock5/rock5b/app-development/rkllm_install
#
# Usage: ./install_rkllm.sh [-y|--yes]
#   -y, --yes    Non-interactive mode, automatically accept prompts

set -e  # Exit on error

# Parse arguments
NON_INTERACTIVE=false
if [[ "$1" == "-y" ]] || [[ "$1" == "--yes" ]]; then
    NON_INTERACTIVE=true
fi

echo "=========================================="
echo "RKLLM Toolkit Installation"
echo "=========================================="
echo ""

# Step 1: Check RKNPU driver version
echo "Step 1: Checking RKNPU driver version..."
if [ -f /sys/kernel/debug/rknpu/version ]; then
    DRIVER_VERSION=$(sudo cat /sys/kernel/debug/rknpu/version)
    echo "Current driver: $DRIVER_VERSION"

    # Check if version is 0.9.8 or higher
    if echo "$DRIVER_VERSION" | grep -q "v0.9.8\|v0.9.9\|v1."; then
        echo "✓ RKNPU driver version is compatible"
    else
        echo "⚠ Warning: RKNPU driver version may be too old"
        echo "  Recommended: v0.9.8 or higher"
        echo "  You may need to update firmware: sudo rsetup → System → System Update"
        if [ "$NON_INTERACTIVE" = false ]; then
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo "  Non-interactive mode: continuing anyway"
        fi
    fi
else
    echo "⚠ Warning: Cannot check RKNPU driver version"
    echo "  File /sys/kernel/debug/rknpu/version not found"
    if [ "$NON_INTERACTIVE" = false ]; then
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "  Non-interactive mode: continuing anyway"
    fi
fi
echo ""

# Step 2: Clone RKNN-LLM repository
echo "Step 2: Cloning RKNN-LLM repository..."
REPO_DIR="rknn-llm"

if [ -d "$REPO_DIR" ]; then
    echo "Repository already exists at $REPO_DIR"
    if [ "$NON_INTERACTIVE" = false ]; then
        read -p "Remove and re-clone? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$REPO_DIR"
        else
            echo "Using existing repository"
        fi
    else
        echo "  Non-interactive mode: using existing repository"
    fi
fi

if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning rknn-llm repository (release-v1.2.1b1)..."
    git clone -b release-v1.2.1b1 https://github.com/airockchip/rknn-llm.git
    echo "✓ Repository cloned successfully"
else
    echo "✓ Repository directory exists"
fi
echo ""

# Step 3: Install RKLLM runtime for ARM64 board
echo "Step 3: Installing RKLLM runtime library..."

# Navigate to the runtime directory
cd "$REPO_DIR/rkllm-runtime/Linux/librkllm_api/aarch64"

# Check if the library exists
if [ ! -f "librkllmrt.so" ]; then
    echo "✗ Error: librkllmrt.so not found in expected location"
    echo "  Expected path: $PWD/librkllmrt.so"
    exit 1
fi

# Install the runtime library to system
echo "Installing runtime library to /usr/lib..."
sudo cp librkllmrt.so /usr/lib/
sudo ldconfig

echo "✓ Runtime library installed"
echo ""

# Step 4: Install Python bindings
echo "Step 4: Installing Python bindings..."
cd ../../../Python/rkllm_binding_demo

# Find the Python wheel file for aarch64
WHEEL_FILE=$(find . -name "rkllm_binding-*.whl" | grep aarch64 | head -1)

if [ -z "$WHEEL_FILE" ]; then
    echo "⚠ Warning: Could not find Python wheel file for aarch64"
    echo "Attempting to install from available wheels..."
    WHEEL_FILE=$(find . -name "rkllm_binding-*.whl" | head -1)
fi

if [ -n "$WHEEL_FILE" ]; then
    echo "Installing: $WHEEL_FILE"
    pip install "$WHEEL_FILE"
    echo "✓ Python bindings installed"
else
    echo "✗ Error: No Python wheel file found"
    echo "  You may need to build the bindings manually"
fi
echo ""

# Step 5: Verify installation
echo "Step 5: Verifying installation..."
cd ../../..
if python3 -c "import rkllm; print('RKLLM module imported successfully')" 2>/dev/null; then
    echo "✓ RKLLM Python module is working"
else
    echo "⚠ Could not import RKLLM Python module"
    echo "  Trying alternative import method..."
    if python3 -c "from rkllm_binding import rkllm; print('RKLLM binding imported successfully')" 2>/dev/null; then
        echo "✓ RKLLM binding is working (alternative import)"
    else
        echo "⚠ Python module verification failed"
        echo "  You may need to adjust PYTHONPATH or install manually"
    fi
fi
echo ""

echo "=========================================="
echo "Installation Summary"
echo "=========================================="
echo "Repository location: $PWD/$REPO_DIR"
echo "Runtime library: /usr/lib/librkllmrt.so"
echo ""
echo "To verify installation, run:"
echo "  python3 -c 'import rkllm; print(\"RKLLM is ready\")'"
echo ""
echo "For examples and documentation, see:"
echo "  $PWD/$REPO_DIR/rkllm-runtime/examples"
echo "=========================================="
