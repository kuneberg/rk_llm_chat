# Installing RKLLM Toolkit

The RKLLM toolkit is a specialized library for Rockchip hardware that is not available on PyPI.

## Installation Options

### Option 1: Check if already installed
On many Rockchip boards, the RKLLM toolkit may already be pre-installed. You can check by running:

```python
python3 -c "from rkllm.api import RKLLM; print('RKLLM is installed')"
```

### Option 2: Install from Rockchip SDK
If not pre-installed, you'll need to install it from the Rockchip SDK:

1. Download the RKLLM SDK from Rockchip's official sources
2. Follow the installation instructions provided in the SDK documentation
3. The typical installation involves copying the Python wheel file and installing it with pip

### Option 3: Manual installation
If you have the RKLLM wheel file:

```bash
pip install /path/to/rkllm_toolkit-*.whl
```

## Verification

After installation, verify it works:

```python
python3 -c "from rkllm.api import RKLLM; print('RKLLM successfully imported')"
```
