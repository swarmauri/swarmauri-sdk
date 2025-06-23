import pytest
from peagen.plugins.mutators.llm_prompt import LlmRewrite


@pytest.mark.unit
def test_llm_prompt_calls_agent(monkeypatch):
    captured = {}

    def fake_call(prompt, env):
        captured["prompt"] = prompt
        captured["env"] = env
        return "out"

    monkeypatch.setattr(
        "peagen.plugins.mutators.llm_prompt.call_external_agent", fake_call
    )
    mut = LlmRewrite({"provider": "dummy"})
    result = mut.mutate("echo hi")
    assert result == "out"
    assert captured["prompt"] == "echo hi"
