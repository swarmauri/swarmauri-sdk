![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_psutil/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_psutil/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_psutil/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_psutil.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_psutil" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_psutil/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_psutil?label=swarmauri_tool_psutil&color=green" alt="PyPI - swarmauri_tool_psutil"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Psutil

`swarmauri_tool_psutil` is a Swarmauri operations tool for retrieving system
telemetry using `psutil`. It exposes CPU, memory, disk, network, and sensor
metrics through a single tool interface, making it useful for observability,
health checks, diagnostics, and agent-driven operations workflows.

## Why Use Swarmauri Tool Psutil

- Expose host telemetry inside Swarmauri agents and automations.
- Retrieve CPU, memory, disk, network, and sensor data on demand.
- Return structured system data without custom psutil glue code.
- Support local diagnostics, service health checks, and runtime audits.

## FAQ

> **What input does the tool expect?**  
> A single `info_type` string: `cpu`, `memory`, `disk`, `network`, or
> `sensors`.

> **What does the tool return?**  
> A dictionary of metrics for the requested system-information family.

> **How are permission-restricted metrics handled?**  
> Network connections and some sensor fields degrade gracefully when access is
> denied.

> **Is it suitable for agents?**  
> Yes. The output is already converted into plain Python objects for easy
> serialization.

## Features

- Swarmauri `ToolBase` implementation registered as `PsutilTool`.
- Collects CPU, memory, disk, network, and sensor metrics.
- Returns plain dictionary/list structures derived from psutil namedtuples.
- Handles common permission or platform gaps for sensors and connections.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_psutil
```

```bash
pip install swarmauri_tool_psutil
```

## Usage

```python
from swarmauri_tool_psutil import PsutilTool

tool = PsutilTool()
cpu = tool("cpu")

print(cpu.keys())
```

## Examples

### Inspect memory metrics

```python
from swarmauri_tool_psutil import PsutilTool

tool = PsutilTool()
memory = tool("memory")

print(memory["virtual_memory"])
```

### Gather network telemetry

```python
from swarmauri_tool_psutil import PsutilTool

tool = PsutilTool()
network = tool("network")

print(network["network_io_counters"])
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_psutil import PsutilTool

tools = ToolCollection(tools=[PsutilTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_webscraping](https://pypi.org/project/swarmauri_tool_webscraping/)
- [swarmauri_tool_zapierhook](https://pypi.org/project/swarmauri_tool_zapierhook/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [psutil documentation](https://psutil.readthedocs.io/)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Expect platform-specific differences in sensor availability.
- Run with elevated privileges only when you truly need restricted telemetry.
- Keep sampling frequency reasonable in long-running monitoring loops.
- Validate `info_type` before invoking the tool from untrusted user input.

## License

This project is licensed under the Apache-2.0 License.
