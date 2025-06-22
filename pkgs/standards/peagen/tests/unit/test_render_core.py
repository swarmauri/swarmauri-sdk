import pytest
from swarmauri_prompt_j2prompttemplate import J2PromptTemplate
from peagen.core.render_core import _render_generate_template


@pytest.mark.unit
def test_render_generate_template_renders_jinja(tmp_path, monkeypatch):
    template_file = tmp_path / "prompt.j2"
    template_file.write_text("Hello {{ name }}")

    j2 = J2PromptTemplate()
    j2.templates_dir = [tmp_path]

    captured = {}

    def fake_agent(prompt, agent_env, cfg=None, logger=None):
        captured["prompt"] = prompt
        return "response"

    monkeypatch.setattr(
        "peagen.core.render_core.call_external_agent",
        fake_agent,
    )

    file_record = {"FILE_NAME": "irrelevant", "RENDERED_FILE_NAME": "out.txt"}
    context = {"name": "World"}

    result = _render_generate_template(
        file_record,
        context,
        str(template_file),
        j2,
        {},
        None,
    )

    assert result == "response"
    assert captured["prompt"] == "Hello World"
