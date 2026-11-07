import pytest
from jsonschema import ValidationError
from swarmauri_agent_runner import AgentRunner, SqliteRunStore
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel


@pytest.mark.unit
def test_resume_after_restart(tmp_path, monkeypatch):
    requests = []

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            if len(requests) == 1:
                return {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call-1",
                                        "type": "function",
                                        "function": {
                                            "name": "AskUserTool",
                                            "arguments": (
                                                '{"prompt":"How many?",'
                                                '"answer_schema":{"type":"integer"}}'
                                            ),
                                        },
                                    },
                                ],
                            }
                        }
                    ]
                }
            return {
                "choices": [
                    {"message": {"role": "assistant", "content": "Received"}}
                ]
            }

    def post(*args, **kwargs):
        requests.append(kwargs["json"])
        return Response()

    monkeypatch.setattr("httpx.post", post)
    path = tmp_path / "runs.db"
    first = AgentRunner(
        OpenAIToolModel(api_key="test").propose_tool_step, SqliteRunStore(path)
    )
    pending = first.start("Ask for a number")
    assert pending.status == "input_required"
    assert len(requests) == 1

    restarted = AgentRunner(
        OpenAIToolModel(api_key="test").propose_tool_step, SqliteRunStore(path)
    )
    question = pending.questions[-1]
    with pytest.raises(ValidationError):
        restarted.resume(
            pending.run_id,
            AnswerMessage(question_id=question.question_id, answer="2"),
        )
    assert restarted.store.load(pending.run_id).status == "input_required"

    answer = AnswerMessage(question_id=question.question_id, answer=2)
    completed = restarted.resume(pending.run_id, answer)
    assert completed.result == "Received"
    assert completed.answers == [answer]
    assert requests[-1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call-1",
        "content": "2",
    }
    with pytest.raises(ValueError, match="no pending question"):
        restarted.resume(pending.run_id, answer)
    assert len(requests) == 2
