![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_conversation_compacting)](https://pepy.tech/projects/swarmauri_conversation_compacting)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_conversation_compacting.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_conversation_compacting)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_conversation_compacting.svg)](https://pypi.org/project/swarmauri_conversation_compacting/)
[![License](https://img.shields.io/pypi/l/swarmauri_conversation_compacting)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_conversation_compacting?label=swarmauri_conversation_compacting&color=green)](https://pypi.org/project/swarmauri_conversation_compacting/)

# Swarmauri Compacting Conversation

Keep a rolling summary of older conversation turns while retaining recent messages for the next model request. Supports Python 3.10 through 3.14.

## Features

- Plans compaction for complete user turns and preserves the newest configured turns.
- Keeps leading system and developer instructions verbatim and checks that tool results match their calls before selecting an older turn.
- Previews compacted context and refuses to apply a stale plan.

## Installation

```sh
uv add --prerelease allow swarmauri_conversation_compacting
pip install --pre swarmauri_conversation_compacting
```

## Usage

```python
from swarmauri_conversation_compacting import CompactingConversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = CompactingConversation(keep_recent_turns=1)
conversation.add_messages([
    HumanMessage(content="Use Python 3.12 for this project."),
    AgentMessage(content="I'll target Python 3.12."),
    HumanMessage(content="What should the project metadata say?"),
])

plan = conversation.plan_compaction()
if plan is not None:
    # In an application, summarize plan.previous_summary and plan.older_messages.
    conversation.apply_compaction(plan, "The project targets Python 3.12.")
```

The model-facing `history` includes the rolling summary. Applying a plan removes the summarized messages from `messages`. Archive the original messages separately if your application needs a complete transcript.

Agents using `AgentCompactionMixin` supply sync and async summarization methods. An adopting agent can set `trigger_tokens` on the conversation and call `compact_if_needed()` or `acompact_if_needed()` before dispatch. Supply a token counter for the request format and include any current instructions and tool definitions.
