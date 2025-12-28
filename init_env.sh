#!/bin/bash
# Initialize virtual environment and install dependencies

set -e  # Exit on error

echo "Initializing RK LLM Chat environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Check if python3-venv is available, if not, try to install it
if ! python3 -m venv --help &> /dev/null; then
    echo "python3-venv is not installed. Attempting to install..."
    if command -v apt &> /dev/null; then
        echo "Installing python3-venv using apt..."
        sudo apt update
        sudo apt install -y python3-venv
    else
        echo "Error: Cannot install python3-venv automatically on this system"
        echo "Please install it manually and run this script again"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found"
fi

echo ""
echo "Environment initialized successfully!"
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the demo, use:"
echo "  python demo.py"
echo ""
echo "For interactive chat, use:"
echo "  python chat.py"
