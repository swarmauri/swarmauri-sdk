import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from jinja2 import Environment
from jinja2.exceptions import SecurityError
from jinja2.sandbox import SandboxedEnvironment
from swarmauri_prompt_j2prompttemplate.J2PromptTemplate import J2PromptTemplate


@pytest.mark.unit
def test_j2prompt_template_type():
    assert J2PromptTemplate().type == "J2PromptTemplate"


@pytest.mark.unit
def test_initialization():
    template = J2PromptTemplate()
    assert isinstance(template.template, str)
    assert isinstance(template.variables, dict)
    assert template.trusted_templates is False
    assert isinstance(template.get_env(), SandboxedEnvironment)


@pytest.mark.unit
def test_set_template_from_string():
    template = J2PromptTemplate()
    template_str = "Hello, {{ name }}!"
    template.set_template(template_str)
    assert template.template == template_str


@pytest.mark.unit
def test_set_template_from_filepath():
    template = J2PromptTemplate()
    with NamedTemporaryFile(delete=False, suffix=".j2") as temp_file:
        temp_file.write(b"Hello, {{ name }}!")
        temp_file_path = temp_file.name

    with open(temp_file_path, "r") as file:
        template_content = file.read()

    template.set_template(template_content)
    assert template.template == template_content
    os.remove(temp_file_path)


@pytest.mark.unit
def test_generate_prompt_from_string_template():
    template = J2PromptTemplate()
    template_str = "Hello, {{ name }}!"
    template.set_template(template_str)
    result = template.generate_prompt({"name": "World"})
    assert result == "Hello, World!"


@pytest.mark.unit
def test_generate_prompt_from_file_template():
    template = J2PromptTemplate()
    with NamedTemporaryFile(delete=False, suffix=".j2") as temp_file:
        temp_file.write(b"Hello, {{ name }}!")
        temp_file_path = temp_file.name

    with open(temp_file_path, "r") as file:
        template_content = file.read()

    template.set_template(template_content)
    result = template.generate_prompt({"name": "World"})
    assert result == "Hello, World!"
    os.remove(temp_file_path)


@pytest.mark.unit
def test_fill_with_variables():
    template = J2PromptTemplate()
    template_str = "Hello, {{ name }}!"
    template.set_template(template_str)
    result = template.fill({"name": "World"})
    assert result == "Hello, World!"


@pytest.mark.unit
def test_split_whitespace():
    result = J2PromptTemplate.split_whitespace("Hello World")
    assert result == ["Hello", "World"]

    result = J2PromptTemplate.split_whitespace("Hello,World", delimiter=",")
    assert result == ["Hello", "World"]

    with pytest.raises(ValueError):
        J2PromptTemplate.split_whitespace(123)


@pytest.mark.unit
def test_default_sandbox_rejects_object_graph_escape():
    template = J2PromptTemplate(
        template="{{ cycler.__init__.__globals__.os.name }}"
    )

    with pytest.raises(SecurityError):
        template.fill()


@pytest.mark.unit
def test_file_template_uses_default_sandbox(tmp_path: Path):
    template_path = tmp_path / "unsafe.j2"
    template_path.write_text(
        "{{ cycler.__init__.__globals__.os.name }}", encoding="utf-8"
    )
    template = J2PromptTemplate(templates_dir=str(tmp_path))
    template.set_template(template_path)

    with pytest.raises(SecurityError):
        template.fill()


@pytest.mark.unit
def test_default_sandbox_rejects_unrestricted_precompiled_template():
    compiled = Environment().from_string("Hello {{ name }}")
    template = J2PromptTemplate(template=compiled)

    with pytest.raises(SecurityError, match="trusted_templates=True"):
        template.fill({"name": "World"})


@pytest.mark.unit
def test_explicit_trusted_mode_preserves_unrestricted_jinja_behavior():
    template = J2PromptTemplate(
        template="{{ cycler.__init__.__globals__.os.name }}",
        trusted_templates=True,
    )

    assert template.fill() == os.name
    assert type(template.get_env()) is Environment
