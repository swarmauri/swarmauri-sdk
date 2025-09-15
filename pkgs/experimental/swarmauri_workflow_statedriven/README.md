![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_workflow_statedriven" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_workflow_statedriven/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_workflow_statedriven.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_workflow_statedriven" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/pypi/l/swarmauri_workflow_statedriven" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_workflow_statedriven/">
        <img src="https://img.shields.io/pypi/v/swarmauri_workflow_statedriven?label=swarmauri_workflow_statedriven&color=green" alt="PyPI - swarmauri_workflow_statedriven"/></a>
</p>

---

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
