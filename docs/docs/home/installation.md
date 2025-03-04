# Installation Guide

This guide covers different ways to install and set up the Swarmauri SDK for your development environment.

## Prerequisites

Before installing Swarmauri SDK, ensure you have:

- Python 3.10 or later
- pip (Python package installer)
- Git (for development installation)

## Quick Installation

### Using pip

```bash
pip install swarmauri
```

### Using Poetry

```bash
poetry add swarmauri
```

## Detailed Installation Methods

### 1. Using pip with Virtual Environment

```bash
# Create a new virtual environment
python -m venv swarmauri_env

# Activate the environment
# On macOS/Linux:
source swarmauri_env/bin/activate

# On Windows:
.\swarmauri_env\Scripts\activate

# Install Swarmauri SDK
pip install swarmauri

# Verify installation
python -c "import swarmauri; print(swarmauri.__version__)"
```

### 2. Using Conda

```bash
# Create a new conda environment
conda create -n swarmauri_env python=3.11

# Activate the environment
conda activate swarmauri_env

# Install pip inside conda environment
conda install pip

# Install Swarmauri SDK
pip install swarmauri

# Optional: Install Jupyter if needed
conda install jupyter
```

### 3. Jupyter Notebook Setup

```bash
# Create a new conda environment with Jupyter
conda create -n swarmauri_jupyter python=3.11 jupyter

# Activate the environment
conda activate swarmauri_jupyter

# Install Swarmauri SDK
pip install swarmauri

# Launch Jupyter Notebook
jupyter notebook
```

## Verification

Verify your installation by running:

```python
import swarmauri

# Check version
print(swarmauri.__version__)

```

## Next Steps

After installation:

1. Check out our [Quickstart Guide](../guide/quickstart.md)
2. Review [API Documentation](../api/index.md)
3. Try our [Examples](../examples/index.md)
4. Join our [Community](../community/index.md)

## Getting Help

If you run into issues:

1. Check our [FAQ](../faq.md)
2. Visit our [GitHub Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
3. Join our [Discord Community](https://discord.gg/swarmauri)