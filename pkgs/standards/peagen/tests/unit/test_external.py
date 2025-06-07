import os
from pathlib import Path
import types
from peagen.core._external import call_external_agent


def test_call_external_agent_reads_peagen_toml(tmp_path, monkeypatch):
    toml_text = """
[llm]
default_provider = "openai"
default_model_name = "gpt-3.5"
default_temperature = 0.3
default_max_tokens = 50

[llm.openai]
API_KEY = "sk-test"
"""
    (tmp_path / ".peagen.toml").write_text(toml_text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    captured = {}

    class DummyLLM:
        pass

    def fake_get_llm(self, provider, api_key=None, model_name=None, **kwargs):
        captured["provider"] = provider
        captured["api_key"] = api_key
        captured["model_name"] = model_name
        return DummyLLM()

    monkeypatch.setattr("peagen.core._llm.GenericLLM.get_llm", fake_get_llm)

    class DummyAgent:
        def __init__(self, llm=None):
            self.llm = llm
            self.conversation = types.SimpleNamespace(system_context=None)

        def exec(self, prompt, llm_kwargs=None):
            captured["llm_kwargs"] = llm_kwargs
            captured["prompt"] = prompt
            return "done"

    monkeypatch.setattr("swarmauri.agents.QAAgent.QAAgent", DummyAgent)
    monkeypatch.setattr(
        "swarmauri.messages.SystemMessage.SystemMessage",
        lambda content: types.SimpleNamespace(content=content),
    )
    monkeypatch.setattr("peagen.core._external.chunk_content", lambda text, logger=None: text)

    result = call_external_agent("hello", {}, logger=None)

    assert result == "done"
    assert captured["provider"] == "openai"
    assert captured["model_name"] == "gpt-3.5"
    assert captured["llm_kwargs"]["max_tokens"] == 50
    assert captured["llm_kwargs"]["temperature"] == 0.3
