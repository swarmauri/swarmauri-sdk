import httpx
import pytest
from swarmauri_core.tool_llms import IToolStepModel, ToolStepResult

from swarmauri_standard.llms.GeminiToolModel import (
    GeminiToolModel as LegacyGemini,
)
from swarmauri_standard.tool_llms.GeminiToolModel import GeminiToolModel


@pytest.mark.parametrize("model_type", [GeminiToolModel, LegacyGemini])
def test_preserves_native_parts_and_correlates_optional_ids(
    model_type, monkeypatch
):
    model = model_type(api_key="test")
    assert isinstance(model, IToolStepModel)
    native = {
        "role": "model",
        "parts": [
            {
                "functionCall": {"id": "native", "name": "echo"},
                "thoughtSignature": "opaque",
            },
            {"functionCall": {"name": "echo"}},
        ],
    }

    def post(url, **_kwargs):
        assert url.endswith(":generateContent")
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"candidates": [{"content": native}]},
        )

    monkeypatch.setattr(httpx, "post", post)
    step = model.propose_step(model.initial_tool_history("Echo"), {})
    assert step.items == [native]
    assert step.calls[0].call_id != step.calls[1].call_id
    response = model.format_tool_results(
        [ToolStepResult(call, None) for call in step.calls]
    )
    assert response == [
        {
            "role": "user",
            "parts": [
                {
                    "functionResponse": {
                        "name": "echo",
                        "id": "native",
                        "response": {"result": None},
                    }
                },
                {
                    "functionResponse": {
                        "name": "echo",
                        "response": {"result": None},
                    }
                },
            ],
        }
    ]
