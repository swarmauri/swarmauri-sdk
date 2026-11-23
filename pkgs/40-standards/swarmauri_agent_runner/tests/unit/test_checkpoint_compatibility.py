import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from threading import Barrier

from swarmauri_agent_runner import (
    AgentRunner,
    ApprovalDecision,
    RunConflictError,
)
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_runstore_sqlite import SqliteRunStore


class Tool(ToolBase):
    name: str = "Review"
    calls: list[int]

    def __call__(self, number):
        self.calls.append(number)
        return number


def model(history, _tools):
    if history[-1]["role"] == "tool":
        return {"role": "assistant", "content": history[-1]["content"]}
    return {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "review",
                "function": {"name": "Review", "arguments": '{"number": 2}'},
            }
        ],
    }


def test_old_database_resumes_and_concurrent_decisions_dispatch_once(tmp_path):
    path = tmp_path / "old.sqlite"
    tool = Tool(calls=[])
    settings = dict(
        tools={tool.name: tool},
        approval_policy=lambda *_: "ask",
        approval_scope="workspace",
    )
    pending = AgentRunner(model, SqliteRunStore(path=path), **settings).start(
        "Review"
    )
    old_fields = {
        "run_id",
        "revision",
        "status",
        "messages",
        "questions",
        "answers",
        "pending_call",
        "approval",
        "result",
    }
    payload = pending.model_dump_json(include=old_fields)
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute(
            "UPDATE runs SET state = ? WHERE id = ?", (payload, pending.run_id)
        )

    barrier = Barrier(2)
    decision = ApprovalDecision(
        approval_id=pending.approval.approval_id, approved=True
    )

    class CompetingRunner(AgentRunner):
        def load(self, run_id):
            state = super().load(run_id)
            if state.status == "approval_required":
                barrier.wait(timeout=5)
            return state

    def decide(_):
        runner = CompetingRunner(model, SqliteRunStore(path=path), **settings)
        try:
            return runner.decide(pending.run_id, decision)
        except RunConflictError:
            return None

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(decide, range(2)))
    assert results.count(None) == 1
    assert tool.calls == [2]
    runner = AgentRunner(model, SqliteRunStore(path=path), **settings)
    state = runner.load(pending.run_id)
    assert state.approval_decisions[decision.approval_id] == decision
    assert state.approval_requests[decision.approval_id] == pending.approval
    assert json.loads(state.messages[-2]["content"]) == 2
