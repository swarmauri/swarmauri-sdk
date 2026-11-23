import pytest

from swarmauri_core.tool_llms import (
    IToolStepModel,
    ProposedToolCall,
    ToolStep,
    ToolStepResult,
)


def test_contract_exposes_provider_items_and_correlated_result():
    call = ProposedToolCall("runner-id", "echo", {"value": 1}, "provider-id")
    item = {"role": "model", "parts": [{"thoughtSignature": "opaque"}]}
    step = ToolStep([item], [call])
    result = ToolStepResult(step.calls[0], {"status": "denied"})
    assert step.items == [item]
    assert result.call.provider_call_id == "provider-id"
    with pytest.raises(TypeError):
        IToolStepModel()
