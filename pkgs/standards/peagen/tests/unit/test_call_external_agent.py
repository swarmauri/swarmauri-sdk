import logging
import pytest

from peagen.core._external import call_external_agent


def test_call_external_agent_redacts_secrets(monkeypatch, caplog):
    class DummyLLM:
        pass

    class DummyAgent:
        def __init__(self, llm=None):
            self.llm = llm
            self.conversation = type("Conv", (), {"system_context": None})()

        def exec(self, prompt, llm_kwargs=None):
            return "dummy-response"

    monkeypatch.setattr(
        "peagen.core._llm.GenericLLM.get_llm",
        lambda self, provider, api_key=None, model_name=None: DummyLLM(),
    )
    monkeypatch.setattr("swarmauri.agents.QAAgent.QAAgent", DummyAgent)

    fake_env = {"provider": "openai", "api_key": "secret123", "model_name": "gpt-4"}

    test_logger = logging.getLogger("peagen_test")
    with caplog.at_level(logging.DEBUG):
        result = call_external_agent("hello", fake_env, logger=test_logger)

    assert result == "dummy-response"
    log_text = "\n".join(record.getMessage() for record in caplog.records)
    assert "secret123" not in log_text
    assert "openai" in log_text
    assert "gpt-4" in log_text
