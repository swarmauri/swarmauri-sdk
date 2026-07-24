from importlib.metadata import entry_points

import pytest
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase

from swarmauri_llm_azureopenai import AzureOpenAIModel, AzureOpenAIToolModel


@pytest.mark.unit
def test_models_directly_use_base_contracts_and_v1_endpoint():
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        api_key="key",
        name="deployment",
    )
    tool_model = AzureOpenAIToolModel(
        endpoint="https://resource.openai.azure.com/openai/v1",
        api_key="key",
        name="deployment",
    )
    assert isinstance(model, LLMBase)
    assert isinstance(tool_model, ToolLLMBase)
    assert model._build_endpoint().endswith("/openai/v1/chat/completions")
    assert tool_model._build_headers()["api-key"] == "key"


@pytest.mark.unit
def test_entra_provider_refreshes_and_is_not_serialized():
    tokens = iter(["token-1", "token-2"])
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        token_provider=lambda: next(tokens),
        name="deployment",
    )
    assert model._build_headers()["Authorization"] == "Bearer token-1"
    assert model._build_headers()["Authorization"] == "Bearer token-2"
    serialized = model.model_dump_json()
    assert "token_provider" not in serialized
    assert "token-" not in serialized


@pytest.mark.unit
def test_entry_points_are_registered():
    assert "AzureOpenAIModel" in {
        entry.name for entry in entry_points(group="swarmauri.llms")
    }
    assert "AzureOpenAIToolModel" in {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
