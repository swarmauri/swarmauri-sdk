![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_toolkit_runtime/">
        <img src="https://static.pepy.tech/badge/swarmauri_toolkit_runtime/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_runtime/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_runtime.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_runtime/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_toolkit_runtime" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_runtime/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_runtime" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_runtime/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_runtime?label=swarmauri_toolkit_runtime&color=green" alt="PyPI - swarmauri_toolkit_runtime"/></a>
</p>
---

# Swarmauri Toolkit RuntimeToolkit

`RuntimeToolkit` is a runtime management toolkit for Swarmauri agents. It exposes agent-callable tools that can create, inspect, list, update, and remove other tools from the active toolkit instance without reaching for a separate plugin manager flow.

## Features

- Bundles agent-callable CRUD operations for toolkit members.
- Accepts serialized tool specs with `type` fields and materializes installed Swarmauri tools at runtime.
- Returns agent-friendly dictionaries for reads, lists, and mutation results.
- Protects the toolkit's own management tools from accidental overwrite or removal.
- Supports Python 3.10 through 3.12.

## Installation

**uv**

```bash
uv add swarmauri_toolkit_runtime
```

**pip**

```bash
pip install swarmauri_toolkit_runtime
```

## Usage

Instantiate the toolkit and hand it to an agent or tool-capable model. The toolkit starts with only its management tools, then grows as the agent adds tools.

```python
from swarmauri_toolkit_runtime import RuntimeToolkit

toolkit = RuntimeToolkit()

toolkit.get_tool_by_name("RegisterRuntimeTool")(
    {
        "type": "AdditionTool",
        "name": "RuntimeAdditionTool",
        "description": "Adds two integers during the active agent session.",
        "parameters": [
            {
                "name": "x",
                "input_type": "integer",
                "description": "The left operand",
                "required": True,
            },
            {
                "name": "y",
                "input_type": "integer",
                "description": "The right operand",
                "required": True,
            },
        ],
    }
)

result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2, 3)
print(result)
```

## Agent Workflow

Typical flow:

1. Call `ListRuntimeTools` to inspect the current runtime surface.
2. Call `RegisterRuntimeTool` with a tool spec to extend the toolkit.
3. Call `InspectRuntimeTool` to inspect the hydrated tool metadata.
4. Call `ReplaceRuntimeTool` when the agent needs to replace a tool with a revised spec.
5. Call `UnregisterRuntimeTool` when a runtime tool should no longer be available.

## Tool Spec Contract

Mutation tools accept a serialized tool specification. At minimum, provide:

- a `type` field that resolves to an installed Swarmauri tool import such as `swarmauri.tools.AdditionTool`
- a non-empty `parameters` list that explicitly declares the runtime callable contract

```python
{
    "type": "AdditionTool",
    "name": "RuntimeAdditionTool",
    "description": "Adds two integers.",
    "parameters": [
        {
            "name": "x",
            "input_type": "integer",
            "description": "The left operand",
            "required": True,
        },
        {
            "name": "y",
            "input_type": "integer",
            "description": "The right operand",
            "required": True,
        },
    ],
}
```

If the target tool defines extra fields, include them in the spec and the toolkit will validate them against the concrete tool class.

## License

`swarmauri_toolkit_runtime` is released under the Apache 2.0 License. See `LICENSE` for details.

