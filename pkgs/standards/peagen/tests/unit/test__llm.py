import random; random.seed(0xA11A)
import types
import importlib
import pytest

from peagen._llm import GenericLLM


@pytest.mark.unit
def test_invalid_provider():
    with pytest.raises(ValueError):
        GenericLLM().get_llm("unknown")


@pytest.mark.unit
def test_valid_provider(monkeypatch):
    class Dummy:
        pass

    mod = types.SimpleNamespace(OpenAIModel=Dummy)
    monkeypatch.setattr(importlib, "import_module", lambda name: mod)
    llm = GenericLLM().get_llm("openai", api_key="key", model_name="gpt")
    assert isinstance(llm, Dummy)
