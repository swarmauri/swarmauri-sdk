![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_zapierhook/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_zapierhook/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_zapierhook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_zapierhook?label=swarmauri_tool_zapierhook&color=green" alt="PyPI - swarmauri_tool_zapierhook"/></a>
</p>
---

# Swarmauri Tool Â· Zapier Hook

A Swarmauri tool that triggers Zapier catch webhooks from within agent workflows. Use it to hand off conversation state to Zapier automationsâ€”send notifications, update CRMs, open tickets, or kick off custom Zaps with a single function call.

- Accepts JSON payloads as strings and posts them to a Zapier webhook URL.
- Surfaces the Zapier HTTP response (success or failure) in a structured dictionary.
- Built on `requests` so you can extend headers, authentication, or timeout behaviour if required.

## Requirements

- Python 3.10 â€“ 3.13.
- A Zapier webhook URL (copy from Zap setup â†’ **Webhooks by Zapier** â†’ **Catch Hook**). Store it securely (environment variables, secrets manager).
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

- **`requests.exceptions.HTTPError`** â€“ Zapier returned a non-200 status (often 401 due to malformed or revoked URLs). Check the webhook URL and payload format.
- **Timeouts or connection errors** â€“ Ensure the environment has outbound internet access and consider wrapping the tool to set explicit timeouts or retries.
- **Zap expects structured JSON** â€“ The tool sends `{"data": payload}`. Adjust your Zapâ€™s â€œCatch Hookâ€ step or extend the tool if you need different envelope fields.

## License

`swarmauri_tool_zapierhook` is released under the Apache 2.0 License. See `LICENSE` for full details.
