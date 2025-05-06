
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_psutil" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_psutil/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_psutil.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_psutil" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_psutil" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_psutil?label=swarmauri_tool_psutil&color=green" alt="PyPI - swarmauri_tool_psutil"/></a>
</p>

---

# Swarmauri Tool Psutil

A system monitoring tool that provides comprehensive system information using psutil library. This tool can gather information about CPU, memory, disk, network, and sensors.

## Installation

```bash
pip install swarmauri_tool_psutil
```

## Usage

Here's a basic example of how to use the PsutilTool:

```python
from swarmauri.tools.PsutilTool import PsutilTool

# Initialize the tool
psutil_tool = PsutilTool()

# Get CPU information
cpu_info = psutil_tool("cpu")
print(cpu_info)  # Shows CPU times, usage percent, frequency, etc.

# Get memory information
memory_info = psutil_tool("memory")
print(memory_info)  # Shows virtual and swap memory details

# Get disk information
disk_info = psutil_tool("disk")
print(disk_info)  # Shows disk partitions, usage, and I/O counters
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

