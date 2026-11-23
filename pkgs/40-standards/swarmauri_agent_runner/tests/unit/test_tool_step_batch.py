import httpx
from swarmauri_agent_runner import AgentRunner, ApprovalDecision
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_standard.tool_llms.GeminiToolModel import GeminiToolModel


class Record(ToolBase):
    name: str = "record"
    calls: list[int]

    def __call__(self, number):
        self.calls.append(number)
        return number


def test_gemini_batch_resumes_after_two_approvals(tmp_path, monkeypatch):
    original = {
        "role": "model",
        "parts": [
            {
                "functionCall": {
                    "name": "record",
                    "id": f"id-{number}",
                    "args": {"number": number},
                },
                **({"thoughtSignature": "signed"} if number == 1 else {}),
            }
            for number in (1, 2, 3)
        ],
    }
    requests = []

    def post(_url, *, json, **_kwargs):
        requests.append(json)
        content = (
            original
            if len(requests) == 1
            else {"role": "model", "parts": [{"text": "Done"}]}
        )
        return httpx.Response(
            200,
            request=httpx.Request("POST", "https://example.com"),
            json={"candidates": [{"content": content}]},
        )

    monkeypatch.setattr(httpx, "post", post)
    path = tmp_path / "run.db"
    tool = Record(calls=[])

    def new_runner():
        return AgentRunner(
            GeminiToolModel(api_key="test"),
            SqliteRunStore(path=path),
            tools={tool.name: tool},
            approval_policy=lambda _, args: (
                "allow" if args["number"] == 1 else "ask"
            ),
            approval_scope="workspace",
        )

    first = new_runner().start("Run")
    assert tool.calls == [1]
    assert first.approval.call_id == "id-2"
    second = new_runner().decide(
        first.run_id,
        ApprovalDecision(
            approval_id=first.approval.approval_id, approved=False
        ),
    )
    assert tool.calls == [1]
    assert second.approval.call_id == "id-3"
    completed = new_runner().decide(
        first.run_id,
        ApprovalDecision(
            approval_id=second.approval.approval_id, approved=True
        ),
    )
    assert tool.calls == [1, 3]
    assert completed.result == "Done"
    assert requests[1]["contents"][1] == original
    responses = [
        part["functionResponse"]
        for part in requests[1]["contents"][2]["parts"]
    ]
    assert [response["id"] for response in responses] == [
        "id-1",
        "id-2",
        "id-3",
    ]
    assert [response["response"]["result"] for response in responses] == [
        1,
        {"status": "denied"},
        3,
    ]
