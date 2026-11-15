# AgentRunner

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_agent_runner)](https://pepy.tech/projects/swarmauri_agent_runner)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_runner.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_runner)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_agent_runner)](https://pypi.org/project/swarmauri_agent_runner/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_runner)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_agent_runner?label=swarmauri_agent_runner&color=green)](https://pypi.org/project/swarmauri_agent_runner/)

Run model tool calls and resume checkpointed human interactions.

## Features

- Run model tool calls and resume checkpointed human interactions.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_agent_runner
pip install swarmauri_agent_runner
```

## Usage

```python
from swarmauri_agent_runner import AgentRunner
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel

model = OpenAIToolModel(api_key="your-api-key")
runner = AgentRunner(model, SqliteRunStore(path="runs.db"))
state = runner.start("Ask me which package to inspect.")
if state.status == "input_required":
    from swarmauri_standard.messages.AnswerMessage import AnswerMessage

    question = state.event().question
    reply = AnswerMessage(question_id=question.question_id, answer=input(question.content))
    state = runner.resume(state.run_id, reply)

```

Reopen the same SQLite database and configure the same model and tools to
resume a pending question or approval in another process. The application
authenticates the caller before exposing a run or accepting a decision.
Set a stable approval scope that identifies the workspace and permissions.
A run interrupted during tool dispatch records that state for reconciliation.
Runtime tool instances and open process handles live in the application process.

## Tool approvals and run stores

Install `swarmauri-runstore-sqlite` to run the SQLite example. The runner
accepts an `IRunStore` and an OpenAI or Gemini tool model. Existing
OpenAI-shaped model callables and legacy typed run stores remain supported.

Set `approval_policy(tool, arguments)` to return `"ask"` for calls that
need review and configure an `approval_scope`. Render `state.event()` in your
application, then submit the authorized reviewer’s decision.

```python
from swarmauri_agent_runner import ApprovalDecision

state = runner.decide(
    run_id,
    ApprovalDecision(approval_id=approval_id, approved=True),
)
```

Use `runner.load(run_id)` to retrieve typed state from a reopened database.
`state.approval_requests` and `state.approval_decisions` retain the information
needed to render resolved approval cards. Tool execution status is separate.
When a process stops during tool dispatch, reconcile the external side effect
before recovering the run.

Existing SQLite databases work with the standalone adapter. The old
`swarmauri_agent_runner.SqliteRunStore` import accepts and returns typed
`RunState` objects. Install `swarmauri_agent_runner[sqlite]` to use that
compatibility wrapper.
