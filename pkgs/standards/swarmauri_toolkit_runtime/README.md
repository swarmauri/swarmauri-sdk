![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_toolkit_runtime/">
        <img src="https://static.pepy.tech/badge/swarmauri_toolkit_runtime/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_runtime/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_runtime.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_runtime/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_runtime/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_runtime" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_runtime/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_runtime?label=swarmauri_toolkit_runtime&color=green" alt="PyPI - swarmauri_toolkit_runtime"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Toolkit RuntimeToolkit

`RuntimeToolkit` is a Swarmauri runtime-management toolkit for agents that need to register, inspect, list, replace, and remove tools during execution. It keeps tool mutation inside the active toolkit instance and requires both explicit parameter declarations and an explicit `__call__` implementation when a new runtime tool is introduced.

## Features

- Bundles agent-callable CRUD operations for toolkit members.
- Accepts serialized runtime tool specs with `type`, `parameters`, and `__call__` fields.
- Enforces a non-empty declared `parameters` list and a non-empty `__call__` body for runtime tool registration and replacement.
- Evaluates runtime `__call__` bodies through a restricted expression rail rather than unrestricted Python execution.
- Returns agent-friendly dictionaries for reads, lists, and mutation results.
- Protects the toolkit's own management tools from accidental overwrite or removal.
- Supports Python 3.10 through 3.12.

## Support

- Python `3.10`
- Python `3.11`
- Python `3.12`

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

Use `RuntimeToolkit` when an agent needs to mutate its own tool surface safely at runtime. The expected workflow is:

1. Start with the management toolkit.
2. Register a runtime tool using an explicit parameter contract and explicit callable body.
3. Inspect or list the available runtime tools.
4. Execute the registered tool.
5. Replace or unregister the tool when the runtime surface changes.

Instantiate the toolkit and hand it to an agent or tool-capable model. The toolkit starts with only its management tools, then grows as the agent adds tools.

```python
from swarmauri_toolkit_runtime import RuntimeToolkit

toolkit = RuntimeToolkit()

toolkit.get_tool_by_name("RegisterRuntimeTool")(
    {
        "type": "RuntimeAdditionTool",
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
        "__call__": '{"sum": str(x + y)}',
    }
)

result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2, 3)
print(result)
```

## Agent Workflow

1. Call `ListRuntimeTools` to inspect the current runtime surface.
2. Call `RegisterRuntimeTool` with a tool spec to extend the toolkit.
3. Call `InspectRuntimeTool` to inspect the hydrated tool metadata.
4. Call `ReplaceRuntimeTool` when the agent needs to replace a tool with a revised spec.
5. Call `UnregisterRuntimeTool` when a runtime tool should no longer be available.

## Tool Spec Contract

Mutation tools accept a serialized tool specification. At minimum, provide:

- a non-empty `type` field that names the runtime tool surface
- a non-empty `parameters` list that explicitly declares the runtime callable contract
- a non-empty `__call__` string that evaluates as a safe Python expression over the declared parameters and approved builtins

The runtime evaluator permits only a constrained expression subset and approved builtins such as `str`, `int`, `float`, `len`, `sum`, `min`, `max`, and `abs`. Imports, attribute traversal, and arbitrary function calls are rejected.

```python
{
    "type": "RuntimeAdditionTool",
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
    "__call__": '{"sum": str(x + y)}',
}
```

The `__call__` value is evaluated against the declared parameter names. A body such as `{"sum": str(x + y)}` is valid. A body that tries to import modules, access attributes, or reference undeclared names is rejected.

## Failure Modes

- Registration fails when the tool spec omits `parameters`.
- Registration fails when the tool spec omits `__call__`.
- Registration fails when the `__call__` body uses unsafe syntax or disallowed names.
- Registration fails when the tool name collides with a protected management tool.
- Execution failures inside an accepted runtime tool return a structured error payload instead of propagating a hard exception or terminating the host process.
- Replacement fails when the target tool is missing, reserved, or renamed to an existing tool.
- Unregistration fails when the target is reserved or absent.

## License

`swarmauri_toolkit_runtime` is released under the Apache 2.0 License. See `LICENSE` for details.



