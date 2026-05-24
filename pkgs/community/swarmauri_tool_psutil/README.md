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

# Swarmauri Tool Â· psutil

A Swarmauri-compatible system inspection tool powered by `psutil`. Use it to surface CPU, memory, disk, network, and sensor telemetry inside agents, observability workflows, or health checks.

- Wraps rich `psutil` APIs behind a single callable interface.
- Returns structured dictionaries that mirror psutil's native data models (converted to plain Python objects for JSON serialization).
- Handles common permission gaps gracefully (e.g., network connections, sensors) so calls do not crash automation.

## Requirements

- Python 3.10 â€“ 3.13.
- `psutil` installed (pulled automatically with the package).
- Optional platform support: some sensor endpoints require root/admin privileges or may not exist on virtualized hosts.

## Installation

Select the installer that matches your environment; each command resolves transitive dependencies.

**pip**

```bash
pip install swarmauri_tool_psutil
```

**Poetry**

```bash
poetry add swarmauri_tool_psutil
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_psutil

# or install directly into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_psutil
```

> Tip: psutil needs native build tooling on some platforms (musl-based containers, Alpine). Install the OS-level prerequisites before running the package install command.

## Quick Start

```python
from pprint import pprint
from swarmauri_tool_psutil import PsutilTool

psutil_tool = PsutilTool()

cpu = psutil_tool("cpu")
mem = psutil_tool("memory")

print("CPU summary:")
pprint(cpu)

print("Memory summary:")
pprint(mem)
```

Each call returns a dictionary keyed by metrics families (e.g., `cpu_times`, `virtual_memory`). Use only the sections you need in downstream automations.

## Usage Scenarios

### Build a Lightweight Health Endpoint

```python
from fastapi import FastAPI
from swarmauri_tool_psutil import PsutilTool

app = FastAPI()
ps_tool = PsutilTool()

@app.get("/health/system")
def system_health():
    return {
        "cpu": ps_tool("cpu"),
        "memory": ps_tool("memory"),
        "disk": ps_tool("disk"),
    }
```

Expose system metrics to dashboards or probes without wiring psutil manually.

### Enrich Swarmauri Agent Responses With Telemetry

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_psutil import PsutilTool

registry = ToolRegistry()
registry.register(PsutilTool())
agent = Agent(tool_registry=registry)

message = HumanMessage(content="report system cpu load and memory usage")
response = agent.run(message)
print(response)
```

Register the tool alongside other Swarmauri capabilities so agents can answer operational questions on demand.

### Archive High-Usage Events for Later Analysis

```python
import json
import time
from pathlib import Path
from swarmauri_tool_psutil import PsutilTool

ps_tool = PsutilTool()
log_dir = Path("telemetry_logs")
log_dir.mkdir(exist_ok=True)

while True:
    snapshot = {
        "ts": time.time(),
        "cpu": ps_tool("cpu"),
        "memory": ps_tool("memory"),
        "network": ps_tool("network"),
    }
    (log_dir / f"snapshot-{int(snapshot['ts'])}.json").write_text(
        json.dumps(snapshot, indent=2)
    )
    time.sleep(60)
```

Capture periodic snapshots that can be loaded into notebooks, dashboards, or anomaly detection jobs.

## Troubleshooting

- **`ValueError: Invalid info_type`** â€“ Only `"cpu"`, `"memory"`, `"disk"`, `"network"`, and `"sensors"` are supported. Validate user input before calling the tool.
- **`Permission denied` retrieving connections/sensors** â€“ Run with elevated privileges or filter out those sections. The tool returns a descriptive string when it cannot access the data.
- **`psutil.AccessDenied` on containerized hosts** â€“ Grant the container additional capabilities (e.g., `SYS_PTRACE`) or restrict to metrics that do not require elevated rights.

## License

`swarmauri_tool_psutil` is released under the Apache 2.0 License. See `LICENSE` for details.


