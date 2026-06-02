![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_workflow_statedriven/">
        <img src="https://static.pepy.tech/badge/swarmauri_workflow_statedriven/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_workflow_statedriven/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_workflow_statedriven.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/pypi/l/swarmauri_workflow_statedriven" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/pypi/v/swarmauri_workflow_statedriven?label=swarmauri_workflow_statedriven&color=green" alt="PyPI - swarmauri_workflow_statedriven"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Workflow Statedriven

An experimental state-driven workflow engine for building graph-based processes using nodes and transitions. It supports conditions, join strategies, merge strategies and input modes to control execution flow.

## Installation

```bash
pip install swarmauri_workflow_statedriven
```

## Usage

```python
from swarmauri_workflow_statedriven.graph import WorkflowGraph

workflow = WorkflowGraph()
# Define nodes and transitions...
result = workflow.execute(start="start", initial_input={})
```

For more details, see the `docs` directory.


