import pytest
from swarmauri_agent_runner import AgentRunner, SqliteRunStore
from swarmauri_agent_runner.ApprovalDecision import ApprovalDecision
from swarmauri_base.tools.ToolBase import ToolBase

pytestmark = pytest.mark.unit


class ExampleTool(ToolBase):
    name: str = "ExampleTool"
    calls: list[int]

    def __call__(self, number: int):
        self.calls.append(number)
        return number


def model(messages, tools):
    if messages[-1]["role"] == "tool":
        return {"role": "assistant", "content": messages[-1]["content"]}
    return {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "test-call",
                "function": {
                    "name": "ExampleTool",
                    "arguments": '{"number": 2}',
                },
            }
        ],
    }


def test_review_is_bound_to_invocation_and_consumed_once(tmp_path):
    store = SqliteRunStore(tmp_path / "run.db")
    tool = ExampleTool(calls=[])
    settings = {
        "tools": {tool.name: tool},
        "approval_policy": lambda *_: "ask",
    }
    runner = AgentRunner(model, store, approval_scope="scope", **settings)
    state = runner.start("Run the example")
    decision = ApprovalDecision(
        approval_id=state.approval.approval_id, approved=True
    )
    assert state.status == "approval_required"
    assert tool.calls == []
    with pytest.raises(ValueError, match="current invocation"):
        AgentRunner(model, store, approval_scope="other", **settings).decide(
            state.run_id,
            decision,
        )
    replacement = ExampleTool(calls=[])
    restarted = AgentRunner(
        model,
        SqliteRunStore(store.path),
        tools={replacement.name: replacement},
        approval_policy=lambda *_: "ask",
        approval_scope="scope",
    )
    assert restarted.decide(state.run_id, decision).result == "2"
    with pytest.raises(ValueError, match="no pending approval"):
        runner.decide(state.run_id, decision)
    assert tool.calls == []
    assert replacement.calls == [2]


def test_denial_does_not_execute(tmp_path):
    store = SqliteRunStore(tmp_path / "run.db")
    tool = ExampleTool(calls=[])
    runner = AgentRunner(
        model,
        store,
        tools={tool.name: tool},
        approval_policy=lambda *_: "ask",
        approval_scope="scope",
    )
    state = runner.start("Run the example")
    decision = ApprovalDecision(
        approval_id=state.approval.approval_id, approved=False
    )
    assert runner.decide(state.run_id, decision).status == "completed"
    assert tool.calls == []
