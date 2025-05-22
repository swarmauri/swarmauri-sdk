import os
from tempfile import NamedTemporaryFile
import pytest
from swarmauri_prompt_j2prompttemplate.J2PromptTemplate import J2PromptTemplate


@pytest.mark.unit
def test_j2prompt_template_type():
    assert J2PromptTemplate().type == "J2PromptTemplate"


@pytest.mark.unit
def test_initialization():
    template = J2PromptTemplate()
    assert isinstance(template.template, str)
    assert isinstance(template.variables, dict)


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
def test_j2pt_singleton_exists():
    from swarmauri_prompt_j2prompttemplate import j2pt

    assert j2pt is not None


@pytest.mark.unit
def test_j2pt_builtin_singular_filter():
    from swarmauri_prompt_j2prompttemplate import j2pt

    # Test the make_singular filter which is always available
    template_str = "{{ 'users' | make_singular }}"
    j2pt.set_template(template_str)
    result = j2pt.fill({})
    assert result == "user"


@pytest.mark.unit
def test_j2pt_builtin_plural_filter():
    from swarmauri_prompt_j2prompttemplate import j2pt

    # Test the make_singular filter which is always available
    template_str = "{{ 'user' | make_plural }}"
    j2pt.set_template(template_str)
    result = j2pt.fill({})
    assert result == "users"


@pytest.mark.unit
def test_j2pt_copy():
    from swarmauri_prompt_j2prompttemplate import j2pt

    # Test basic copy functionality
    copy_instance = j2pt.model_copy(deep=False)
    assert copy_instance is not j2pt

    # Test templates_dir handling
    original_dir = j2pt.templates_dir
    j2pt.templates_dir = ["test_dir"]
    copy_with_dir = j2pt.model_copy(deep=False)
    assert copy_with_dir.templates_dir == ["test_dir"]

    # Restore original
    j2pt.templates_dir = original_dir
