# Swarmauri CompactingAgent

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_agent_compacting)](https://pepy.tech/projects/swarmauri_agent_compacting)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_compacting.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_compacting)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_agent_compacting)](https://pypi.org/project/swarmauri_agent_compacting/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_compacting)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_agent_compacting?label=swarmauri_agent_compacting&color=green)](https://pypi.org/project/swarmauri_agent_compacting/)

Run text conversations that keep recent turns and summarize older complete turns. Supports Python 3.10 through 3.12.

## Features

- Use `compact()` or `acompact()` to attempt manual compaction.
- Set `trigger_tokens` on `CompactingConversation` to check the threshold after appending input and before dispatch from `exec()` or `aexec()`.
- Reuse the chat model for summarization or supply a dedicated text model and its own generation options.
- Set `max_input_tokens` to enforce an input budget after the compaction check.

## Installation

```sh
uv add --prerelease allow swarmauri_agent_compacting
pip install --pre swarmauri_agent_compacting
```

## Usage

Supply a Swarmauri text model that appends its reply to the conversation, and a token counter for that model's input format.

```python
from swarmauri_agent_compacting import CompactingAgent
from swarmauri_conversation_compacting import CompactingConversation


def make_agent(model, count_tokens):
    return CompactingAgent(
        llm=model,
        conversation=CompactingConversation(
            trigger_tokens=24_000,
            keep_recent_turns=4,
        ),
        count_input_tokens=count_tokens,
        max_input_tokens=28_000,
    )


def run_turn(agent, prompt):
    reply = agent.exec(prompt)
    changed = agent.compact()
    return reply, changed


async def run_turn_async(agent, prompt):
    reply = await agent.aexec(prompt)
    changed = await agent.acompact()
    return reply, changed
```

Omit `trigger_tokens` for manual-only use. Compaction returns `True` when a shorter summary is applied. The token counter is runtime configuration. Pass it again when restoring the agent from serialized data.

Each agent owns one conversation. Use sequential calls for that conversation. `batch()` and `abatch()` process turns in order. A budget error leaves the pending message in the conversation so you can retry with `exec()` or `aexec()` without appending it again.
