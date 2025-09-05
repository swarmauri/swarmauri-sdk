import pytest
from peagen.plugins.mutators.llm_prog_rewrite import LlmProgRewrite
from swarmauri_standard.programs.Program import Program


@pytest.mark.unit
def test_llm_prog_rewrite_formats_prompt(monkeypatch):
    captured = {}

    def fake_call(prompt, env):
        captured["prompt"] = prompt
        captured["env"] = env
        return "out"

    monkeypatch.setattr(
        "peagen.plugins.mutators.llm_prog_rewrite.call_external_agent", fake_call
    )
    prog = Program(content={"a.py": "print(1)"})
    mut = LlmProgRewrite({"provider": "dummy"})
    result = mut.mutate("echo {parent}", parent_program=prog)
    assert result == "out"
    assert "print(1)" in captured["prompt"]
