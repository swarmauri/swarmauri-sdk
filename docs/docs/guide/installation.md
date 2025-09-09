# Installation Guide

This guide covers different ways to install and set up the Swarmauri SDK for your development environment.

!!! info "Prerequisites"
    Before installing Swarmauri SDK, ensure you have:

    - Python 3.8 or later
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

## Dependency Management

!!! tip "Dependency Options"
    Swarmauri has a modular architecture with minimal core dependencies:

    ```bash
    # Install core package only
    pip install swarmauri

    # Install with recommended tools
    pip install swarmauri[standard]

    # Install all optional packages
    pip install swarmauri[all]
    ```

### Community Packages

Install community-contributed packages as needed:

```bash
pip install swarmauri_tool_jupytertoolkit
pip install swarmauri_vectorstore_pgvector
```

## Troubleshooting Common Issues

???+ warning "Common Installation Problems" 
    ### Import Errors

    If you see `ModuleNotFoundError`:

    ```bash
    # Make sure you've installed the necessary packages
    pip list | grep swarmauri
    ```

    ### Version Conflicts

    If you encounter dependency conflicts:

    ```bash
    # Create a fresh virtual environment
    python -m venv fresh-env
    source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows
    pip install swarmauri
    ```

    ### Installation Fails

    If installation fails with build errors:

    ```bash
    # Install build tools
    # On Windows:
    pip install --upgrade setuptools wheel

    # On macOS/Linux:
    pip install --upgrade setuptools wheel
    sudo apt install build-essential  # For Ubuntu/Debian
    ```

## Advanced Installation Options

### Developer Installation

For contributors:

```bash
# Clone the repository
git clone https://github.com/swarmauri/swarmauri-sdk.git
cd swarmauri-sdk

# Install in development mode
pip install -e .
```

## Environment Configuration

!!! danger "API Key Security"
    Never commit API keys to version control or share them publicly.

    Set up API keys and configurations:

    ```bash
    # Set environment variables
    # On Windows:
    set OPENAI_API_KEY=your-key-here

    # On macOS/Linux:
    export OPENAI_API_KEY=your-key-here
    ```

    Or create a .env file:

    ```env
    OPENAI_API_KEY=your-key-here
    ANTHROPIC_API_KEY=your-key-here
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

1. Check out our Quickstart Guide
2. Review API Documentation
3. Try our Examples
4. Join our Community

!!! question "Need Help?"
    If you run into issues:

    1. Check our FAQ
    2. Visit our [GitHub Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
    3. Join our [Discord Community](https://discord.gg/swarmauri)
