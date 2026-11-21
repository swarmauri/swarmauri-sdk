import httpx
import pytest
from swarmauri_core.tool_llms import IToolStepModel, ToolStepResult

from swarmauri_standard.llms.OpenAIToolModel import (
    OpenAIToolModel as LegacyOpenAI,
)
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel


@pytest.mark.parametrize("model_type", [OpenAIToolModel, LegacyOpenAI])
def test_proposal_round_trips_without_dispatch(model_type, monkeypatch):
    model = model_type(api_key="test")
    assert isinstance(model, IToolStepModel)
    proposal = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": "echo", "arguments": "{}"},
            }
        ],
    }
    received = []

    def post(url, *, json, **_kwargs):
        received.append(json)
        assert url.endswith("/chat/completions")
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"choices": [{"message": proposal}]},
        )

    monkeypatch.setattr(httpx, "post", post)
    history = model.initial_tool_history("Echo")
    step = model.propose_step(history, {})
    output = model.format_tool_results(
        [ToolStepResult(step.calls[0], {"status": "denied"})]
    )
    model.propose_step(history + step.items + output, {})
    assert received[1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call-1",
        "content": '{"status": "denied"}',
    }
