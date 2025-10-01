![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_zapierhook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_zapierhook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_zapierhook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_zapierhook?label=swarmauri_tool_zapierhook&color=green" alt="PyPI - swarmauri_tool_zapierhook"/></a>
</p>

---

# Swarmauri Tool · Zapier Hook

A Swarmauri tool that triggers Zapier catch webhooks from within agent workflows. Use it to hand off conversation state to Zapier automations—send notifications, update CRMs, open tickets, or kick off custom Zaps with a single function call.

- Accepts JSON payloads as strings and posts them to a Zapier webhook URL.
- Surfaces the Zapier HTTP response (success or failure) in a structured dictionary.
- Built on `requests` so you can extend headers, authentication, or timeout behaviour if required.

## Requirements

- Python 3.10 – 3.13.
- A Zapier webhook URL (copy from Zap setup → **Webhooks by Zapier** → **Catch Hook**). Store it securely (environment variables, secrets manager).
- Dependencies (`requests`, `swarmauri_base`, `swarmauri_standard`, `pydantic`) install automatically with the package.

## Installation

Pick the packaging workflow that fits your project; each command installs dependencies.

**pip**

```bash
pip install swarmauri_tool_zapierhook
```

**Poetry**

```bash
poetry add swarmauri_tool_zapierhook
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_zapierhook

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_zapierhook
```

> Tip: Treat the webhook URL like a secret. Avoid hardcoding it in source control and prefer environment variables.

## Quick Start

```python
import json
import os
from swarmauri_tool_zapierhook import ZapierHookTool

zap_url = os.environ["ZAPIER_WEBHOOK_URL"]
zap_tool = ZapierHookTool(zap_url=zap_url)

payload = json.dumps({
    "message": "Hello from Swarmauri!",
    "source": "webhook-demo"
})

result = zap_tool(payload)
print(result["zap_response"])
```

`ZapierHookTool` wraps the payload in a JSON object (`{"data": payload}`) before posting, matching the expectations of most Zapier catch hooks.

## Usage Scenarios

### Forward Agent Decisions to Zapier

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_zapierhook import ZapierHookTool

registry = ToolRegistry()
registry.register(ZapierHookTool(zap_url=os.environ["ZAPIER_WEBHOOK_URL"]))
agent = Agent(tool_registry=registry)

message = HumanMessage(content="log a follow-up task for the sales team")
response = agent.run(message)
print(response)
```

The agent can serialize conversation context, send it to Zapier, and continue the dialogue with confirmation details.

### Escalate Incidents From Monitoring Scripts

```python
import json
import os
from swarmauri_tool_zapierhook import ZapierHookTool

zap_tool = ZapierHookTool(zap_url=os.environ["INCIDENT_ZAP_URL"])
alert = {
    "service": "payments",
    "severity": "critical",
    "message": "Latency exceeded threshold"
}

result = zap_tool(json.dumps(alert))
print("Zapier response:", result["zap_response"])
```

Trigger a Zap that files tickets, posts to Slack, or updates status pages when your monitoring detects issues.

### Batch Replay Events

```python
import json
import os
from swarmauri_tool_zapierhook import ZapierHookTool

zap_tool = ZapierHookTool(zap_url=os.environ["EVENT_ZAP_URL"])
with open("events.json") as fh:
    events = json.load(fh)

for event in events:
    payload = json.dumps(event)
    zap_tool(payload)
```

Replay queued events into Zapier when systems come back online.

## Troubleshooting

- **`requests.exceptions.HTTPError`** – Zapier returned a non-200 status (often 401 due to malformed or revoked URLs). Check the webhook URL and payload format.
- **Timeouts or connection errors** – Ensure the environment has outbound internet access and consider wrapping the tool to set explicit timeouts or retries.
- **Zap expects structured JSON** – The tool sends `{"data": payload}`. Adjust your Zap’s “Catch Hook” step or extend the tool if you need different envelope fields.

## License

`swarmauri_tool_zapierhook` is released under the Apache 2.0 License. See `LICENSE` for full details.
