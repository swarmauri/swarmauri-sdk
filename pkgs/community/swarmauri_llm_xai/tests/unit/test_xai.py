from importlib.metadata import entry_points

import pytest
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase

from swarmauri_llm_xai import XAIModel, XAIToolModel


@pytest.mark.unit
def test_models_directly_use_base_contracts():
    model = XAIModel(api_key="key")
    tool_model = XAIToolModel(api_key="key")
    assert isinstance(model, LLMBase)
    assert isinstance(tool_model, ToolLLMBase)
    assert model._build_endpoint() == "https://api.x.ai/v1/chat/completions"
    assert tool_model._build_headers()["Authorization"] == "Bearer key"


@pytest.mark.unit
def test_credentials_are_not_serialized():
    model = XAIModel(api_key="secret")
    serialized = model.model_dump_json()
    assert "api_key" not in serialized
    assert "secret" not in serialized


@pytest.mark.unit
def test_entry_points_are_registered():
    assert "XAIModel" in {
        entry.name for entry in entry_points(group="swarmauri.llms")
    }
    assert "XAIToolModel" in {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
